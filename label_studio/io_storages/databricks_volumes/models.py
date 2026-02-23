"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""

import io
import json
import logging
import os
import types
from typing import Union

from core.redis import start_job_async_or_sync
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from io_storages.base_models import (
    ExportStorage,
    ExportStorageLink,
    ImportStorage,
    ImportStorageLink,
    ProjectStorageMixin,
)
from io_storages.databricks_volumes.utils import DatabricksVolumes
from io_storages.utils import StorageObject, load_tasks_json, parse_range, storage_can_resolve_bucket_url
from tasks.models import Annotation

logger = logging.getLogger(__name__)


class DatabricksVolumesStorageMixin(models.Model):
    databricks_host = models.TextField(
        _('databricks_host'),
        null=True,
        blank=True,
        help_text='Databricks workspace URL (e.g. https://dbc-xxx.cloud.databricks.com)',
    )
    databricks_client_id = models.TextField(
        _('databricks_client_id'),
        null=True,
        blank=True,
        help_text='Databricks Service Principal client ID',
    )
    databricks_client_secret = models.TextField(
        _('databricks_client_secret'),
        null=True,
        blank=True,
        help_text='Databricks Service Principal OAuth secret',
    )
    catalog = models.TextField(
        _('catalog'),
        null=True,
        blank=True,
        help_text='Unity Catalog catalog name',
    )
    schema_name = models.TextField(
        _('schema_name'),
        null=True,
        blank=True,
        help_text='Unity Catalog schema name',
    )
    volume = models.TextField(
        _('volume'),
        null=True,
        blank=True,
        help_text='Unity Catalog volume name',
    )
    prefix = models.TextField(
        _('prefix'),
        null=True,
        blank=True,
        help_text='Path prefix within the volume',
    )
    regex_filter = models.TextField(
        _('regex_filter'),
        null=True,
        blank=True,
        help_text='Cloud storage regex for filtering objects',
    )
    use_blob_urls = models.BooleanField(
        _('use_blob_urls'),
        default=False,
        help_text='Interpret objects as BLOBs and generate URLs',
    )

    @property
    def bucket(self):
        """Return a bucket-like identifier for URL resolution compatibility.

        Used by storage_can_resolve_bucket_url() to match uc-volumes://<bucket>/path URIs.
        """
        return f'{self.catalog}.{self.schema_name}.{self.volume}'

    def get_client(self):
        return DatabricksVolumes.get_client(
            self.databricks_host,
            self.databricks_client_id,
            self.databricks_client_secret,
        )

    def validate_connection(self):
        DatabricksVolumes.validate_connection(
            self.databricks_host,
            self.databricks_client_id,
            self.databricks_client_secret,
            self.catalog,
            self.schema_name,
            self.volume,
            # don't validate prefix for export storage, it will be created automatically
            None if 'Export' in self.__class__.__name__ else self.prefix,
        )

    def get_volume_path(self, key=None):
        return DatabricksVolumes.get_volume_path(
            self.catalog,
            self.schema_name,
            self.volume,
            prefix=self.prefix,
            key=key,
        )

    def get_bytes_stream(self, uri, range_header=None):
        """Get file bytes from Databricks Volumes as a streaming object with metadata.

        Returns a tuple of (stream, content_type, metadata_dict).
        """
        from urllib.parse import urlparse

        parsed_uri = urlparse(uri, allow_fragments=False)
        bucket = parsed_uri.netloc  # catalog.schema.volume
        blob_name = parsed_uri.path.lstrip('/')

        try:
            parts = bucket.split('.')
            if len(parts) != 3:
                raise ValueError(f'Invalid uc-volumes bucket format: {bucket}')
            cat, sch, vol = parts

            client = self.get_client()
            volume_path = DatabricksVolumes.get_volume_path(cat, sch, vol, key=blob_name)
            data = DatabricksVolumes.read_file(client, volume_path)

            start, end = parse_range(range_header)
            total_size = len(data)

            if start is None and end is None:
                start, end = 0, total_size
            if start == 0 and (end == 0 or end == ''):
                start, end = 0, 1

            if isinstance(end, str) and end == '':
                end = total_size

            chunk = data[start:end]
            stream = io.BytesIO(chunk)

            # Add iter_chunks() and close() methods expected by the proxy's time_limited_chunker
            def _iter_chunks(self_stream, chunk_size=256 * 1024):
                while True:
                    buf = self_stream.read(chunk_size)
                    if not buf:
                        break
                    yield buf

            stream.iter_chunks = types.MethodType(_iter_chunks, stream)

            # Determine content type from extension
            content_type = 'application/octet-stream'
            if blob_name.endswith('.json'):
                content_type = 'application/json'
            elif blob_name.endswith('.jpg') or blob_name.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif blob_name.endswith('.png'):
                content_type = 'image/png'

            metadata = {
                'ETag': '',
                'ContentLength': len(chunk),
                'ContentRange': f'bytes {start}-{end}/{total_size}',
                'LastModified': None,
                'StatusCode': 206 if (start > 0 or end < total_size) else 200,
            }
            return stream, content_type, metadata

        except Exception as e:
            logger.error(f'Error getting stream from Databricks Volumes for uri {uri}: {e}', exc_info=True)
            return None, None, {}

    class Meta:
        abstract = True


class DatabricksVolumesImportStorageBase(DatabricksVolumesStorageMixin, ImportStorage):
    url_scheme = 'uc-volumes'

    # Unity Catalog Volumes doesn't support presigned URLs;
    # all file access is proxied through Label Studio.
    presign = False

    recursive_scan = models.BooleanField(
        _('recursive scan'),
        default=False,
        db_default=False,
        null=True,
        help_text=_('Perform recursive scan over the volume content'),
    )

    def iter_objects(self):
        return DatabricksVolumes.iter_files(
            client=self.get_client(),
            catalog=self.catalog,
            schema_name=self.schema_name,
            volume=self.volume,
            prefix=self.prefix,
            regex_filter=self.regex_filter,
            recursive_scan=bool(self.recursive_scan),
        )

    def iter_keys(self):
        for obj in self.iter_objects():
            # obj.path is the full /Volumes/... path; extract the relative key
            volume_base = DatabricksVolumes.get_volume_path(self.catalog, self.schema_name, self.volume)
            key = obj.path
            if key.startswith(volume_base):
                key = key[len(volume_base) :].lstrip('/')
            yield key

    def get_unified_metadata(self, obj):
        volume_base = DatabricksVolumes.get_volume_path(self.catalog, self.schema_name, self.volume)
        key = obj.path
        if key.startswith(volume_base):
            key = key[len(volume_base) :].lstrip('/')
        return {
            'key': key,
            'last_modified': getattr(obj, 'last_modified', None),
            'size': getattr(obj, 'file_size', None),
        }

    def get_data(self, key) -> list[StorageObject]:
        if self.use_blob_urls:
            task = {settings.DATA_UNDEFINED_NAME: DatabricksVolumes.get_uri(self.catalog, self.schema_name, self.volume, key)}
            return [StorageObject(key=key, task_data=task)]
        blob = DatabricksVolumes.read_file(
            client=self.get_client(),
            volume_path=self.get_volume_path(key=key),
        )
        return load_tasks_json(blob, key)

    def generate_http_url(self, url):
        # Unity Catalog Volumes doesn't support presigned URLs.
        # All file access is proxied through Label Studio.
        return url

    def can_resolve_url(self, url: Union[str, None]) -> bool:
        return storage_can_resolve_bucket_url(self, url)

    def scan_and_create_links(self):
        return self._scan_and_create_links(DatabricksVolumesImportStorageLink)

    class Meta:
        abstract = True


class DatabricksVolumesImportStorage(ProjectStorageMixin, DatabricksVolumesImportStorageBase):
    class Meta:
        abstract = False


class DatabricksVolumesExportStorage(DatabricksVolumesStorageMixin, ExportStorage):
    def save_annotation(self, annotation):
        logger.debug(f'Creating new object on {self.__class__.__name__} Storage {self} for annotation {annotation}')
        ser_annotation = self._get_serialized_data(annotation)

        # get key that identifies this object in storage
        key = DatabricksVolumesExportStorageLink.get_key(annotation)
        volume_path = self.get_volume_path(key=key)

        # put object into storage
        client = self.get_client()
        DatabricksVolumes.upload_file(client, volume_path, json.dumps(ser_annotation).encode('utf-8'))

        # create link if everything ok
        DatabricksVolumesExportStorageLink.create(annotation, self)

    def delete_annotation(self, annotation):
        logger.debug(f'Deleting object on {self.__class__.__name__} Storage {self} for annotation {annotation}')
        key = DatabricksVolumesExportStorageLink.get_key(annotation)
        volume_path = self.get_volume_path(key=key)

        client = self.get_client()
        try:
            DatabricksVolumes.delete_file(client, volume_path)
        except Exception:
            logger.warning(f'Failed to delete {volume_path} for annotation {annotation}')


def async_export_annotation_to_databricks_volumes_storages(annotation):
    project = annotation.project
    if hasattr(project, 'io_storages_databricksvolumesexportstorages'):
        for storage in project.io_storages_databricksvolumesexportstorages.all():
            logger.debug(f'Export {annotation} to Databricks Volumes storage {storage}')
            storage.save_annotation(annotation)


@receiver(post_save, sender=Annotation)
def export_annotation_to_databricks_volumes_storages(sender, instance, **kwargs):
    storages = getattr(instance.project, 'io_storages_databricksvolumesexportstorages', None)
    if storages and storages.exists():  # avoid excess jobs in rq
        start_job_async_or_sync(async_export_annotation_to_databricks_volumes_storages, instance)


@receiver(pre_delete, sender=Annotation)
def delete_annotation_from_databricks_volumes_storages(sender, instance, **kwargs):
    links = DatabricksVolumesExportStorageLink.objects.filter(annotation=instance)
    for link in links:
        storage = link.storage
        if storage.can_delete_objects:
            logger.debug(f'Delete {instance} from Databricks Volumes storage {storage}')
            storage.delete_annotation(instance)


class DatabricksVolumesImportStorageLink(ImportStorageLink):
    storage = models.ForeignKey(DatabricksVolumesImportStorage, on_delete=models.CASCADE, related_name='links')


class DatabricksVolumesExportStorageLink(ExportStorageLink):
    storage = models.ForeignKey(DatabricksVolumesExportStorage, on_delete=models.CASCADE, related_name='links')

    @staticmethod
    def get_key(annotation):
        """Generate an export key based on the source filename.

        Produces keys like ``source_file_name_label.json``.  When the source
        filename cannot be determined (e.g. the task was not imported from a
        Databricks volume or has no recognisable file URI), falls back to
        ``task_<id>_label.json``.
        """
        source_name = None

        # Try the import storage link first — its key is the relative path
        # within the volume (e.g. "images/photo.jpg").
        try:
            link = annotation.task.io_storages_databricksvolumesimportstoragelink
            if link and link.key:
                source_name = os.path.basename(link.key)
        except Exception:
            pass

        # Fallback: scan task.data values for a uc-volumes:// URI.
        if not source_name:
            try:
                for value in annotation.task.data.values():
                    if isinstance(value, str) and value.startswith('uc-volumes://'):
                        source_name = value.rsplit('/', 1)[-1]
                        break
            except Exception:
                pass

        if source_name:
            stem = os.path.splitext(source_name)[0]
        else:
            stem = f'task_{annotation.task.id}'

        return f'{stem}_label.json'
