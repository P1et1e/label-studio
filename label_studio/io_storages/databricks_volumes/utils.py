"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""

import io
import logging
import re

from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


class DatabricksVolumes:
    _client_cache = {}

    @classmethod
    def get_client(cls, databricks_host, client_id, client_secret):
        """Create or return a cached WorkspaceClient for the given credentials.

        The Databricks SDK handles OAuth token exchange and refresh automatically.
        """
        cache_key = f'{databricks_host}:{client_id}'
        if cache_key not in cls._client_cache:
            cls._client_cache[cache_key] = WorkspaceClient(
                host=databricks_host,
                client_id=client_id,
                client_secret=client_secret,
            )
        return cls._client_cache[cache_key]

    @classmethod
    def validate_connection(cls, databricks_host, client_id, client_secret, catalog, schema_name, volume, prefix=None):
        """Validate that we can connect and access the specified volume."""
        logger.debug('Validating Databricks Volumes connection')
        client = cls.get_client(databricks_host, client_id, client_secret)
        volume_path = cls.get_volume_path(catalog, schema_name, volume, prefix=prefix)
        logger.debug(f'Listing contents of {volume_path}')
        # This will raise if the path doesn't exist or credentials are invalid
        list(client.files.list_directory_contents(volume_path))

    @classmethod
    def iter_files(cls, client, catalog, schema_name, volume, prefix=None, regex_filter=None, recursive_scan=True):
        """Iterate over files in a Unity Catalog Volume.

        Yields dicts with 'name', 'last_modified', 'size', 'is_directory' keys.
        """
        volume_path = cls.get_volume_path(catalog, schema_name, volume, prefix=prefix)
        regex = re.compile(str(regex_filter)) if regex_filter else None
        yield from cls._iter_path(client, volume_path, regex, recursive_scan)

    @classmethod
    def _iter_path(cls, client, path, regex, recursive_scan):
        """Recursively iterate files under a given path."""
        for entry in client.files.list_directory_contents(path):
            if entry.is_directory:
                if recursive_scan:
                    yield from cls._iter_path(client, entry.path, regex, recursive_scan)
                continue

            if regex and not regex.match(entry.path):
                logger.debug(f'{entry.path} is skipped by regex filter')
                continue

            yield entry

    @classmethod
    def read_file(cls, client, volume_path):
        """Download file bytes from a Unity Catalog Volume."""
        response = client.files.download(volume_path)
        return response.contents.read()

    @classmethod
    def upload_file(cls, client, volume_path, data, overwrite=True):
        """Upload data to a Unity Catalog Volume.

        The Databricks SDK expects a BinaryIO (file-like) object for the contents parameter.
        """
        if isinstance(data, bytes):
            data = io.BytesIO(data)
        client.files.upload(volume_path, data, overwrite=overwrite)

    @classmethod
    def delete_file(cls, client, volume_path):
        """Delete a file from a Unity Catalog Volume."""
        client.files.delete(volume_path)

    @classmethod
    def get_volume_path(cls, catalog, schema_name, volume, prefix=None, key=None):
        """Build a /Volumes/<catalog>/<schema>/<volume>[/<prefix>][/<key>] path."""
        path = f'/Volumes/{catalog}/{schema_name}/{volume}'
        if prefix:
            path = f'{path}/{prefix.strip("/")}'
        if key:
            path = f'{path}/{key.strip("/")}'
        return path

    @classmethod
    def get_uri(cls, catalog, schema_name, volume, key):
        """Build a uc-volumes://<catalog>.<schema>.<volume>/<key> URI."""
        return f'uc-volumes://{catalog}.{schema_name}.{volume}/{key}'
