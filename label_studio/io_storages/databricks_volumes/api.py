"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""

from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from io_storages.api import (
    ExportStorageDetailAPI,
    ExportStorageFormLayoutAPI,
    ExportStorageListAPI,
    ExportStorageSyncAPI,
    ExportStorageValidateAPI,
    ImportStorageDetailAPI,
    ImportStorageFormLayoutAPI,
    ImportStorageListAPI,
    ImportStorageSyncAPI,
    ImportStorageValidateAPI,
)
from io_storages.databricks_volumes.models import DatabricksVolumesExportStorage, DatabricksVolumesImportStorage
from io_storages.databricks_volumes.serializers import (
    DatabricksVolumesExportStorageSerializer,
    DatabricksVolumesImportStorageSerializer,
)

from .openapi_schema import (
    _databricks_volumes_export_storage_schema,
    _databricks_volumes_export_storage_schema_with_id,
    _databricks_volumes_import_storage_schema,
    _databricks_volumes_import_storage_schema_with_id,
)


@method_decorator(
    name='get',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Get all import storage',
        description='Get a list of all Databricks Unity Catalog Volumes import storage connections.',
        parameters=[
            OpenApiParameter(
                name='project',
                type=OpenApiTypes.INT,
                location='query',
                description='Project ID',
                required=True,
            ),
        ],
        request=None,
        extensions={
            'x-fern-sdk-group-name': ['import_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'list',
            'x-fern-audiences': ['public'],
        },
    ),
)
@method_decorator(
    name='post',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Create import storage',
        description='Create a new Databricks Unity Catalog Volumes import storage connection.',
        request={
            'application/json': _databricks_volumes_import_storage_schema,
        },
        extensions={
            'x-fern-sdk-group-name': ['import_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'create',
            'x-fern-audiences': ['public'],
        },
    ),
)
class DatabricksVolumesImportStorageListAPI(ImportStorageListAPI):
    queryset = DatabricksVolumesImportStorage.objects.all()
    serializer_class = DatabricksVolumesImportStorageSerializer


@method_decorator(
    name='get',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Get import storage',
        description='Get a specific Databricks Unity Catalog Volumes import storage connection.',
        request=None,
        extensions={
            'x-fern-sdk-group-name': ['import_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'get',
            'x-fern-audiences': ['public'],
        },
    ),
)
@method_decorator(
    name='patch',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Update import storage',
        description='Update a specific Databricks Unity Catalog Volumes import storage connection.',
        request={
            'application/json': _databricks_volumes_import_storage_schema,
        },
        extensions={
            'x-fern-sdk-group-name': ['import_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'update',
            'x-fern-audiences': ['public'],
        },
    ),
)
@method_decorator(
    name='delete',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Delete import storage',
        description='Delete a specific Databricks Unity Catalog Volumes import storage connection.',
        request=None,
        extensions={
            'x-fern-sdk-group-name': ['import_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'delete',
            'x-fern-audiences': ['public'],
        },
    ),
)
class DatabricksVolumesImportStorageDetailAPI(ImportStorageDetailAPI):
    queryset = DatabricksVolumesImportStorage.objects.all()
    serializer_class = DatabricksVolumesImportStorageSerializer


@method_decorator(
    name='post',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Sync import storage',
        description='Sync tasks from a Databricks Unity Catalog Volumes import storage connection.',
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location='path',
                description='Storage ID',
            ),
        ],
        request=None,
        extensions={
            'x-fern-sdk-group-name': ['import_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'sync',
            'x-fern-audiences': ['public'],
        },
    ),
)
class DatabricksVolumesImportStorageSyncAPI(ImportStorageSyncAPI):
    serializer_class = DatabricksVolumesImportStorageSerializer


@method_decorator(
    name='post',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Sync export storage',
        description='Sync tasks from a Databricks Unity Catalog Volumes export storage connection.',
        request=None,
        extensions={
            'x-fern-sdk-group-name': ['export_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'sync',
            'x-fern-audiences': ['public'],
        },
    ),
)
class DatabricksVolumesExportStorageSyncAPI(ExportStorageSyncAPI):
    serializer_class = DatabricksVolumesExportStorageSerializer


@method_decorator(
    name='post',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Validate import storage',
        description='Validate a specific Databricks Unity Catalog Volumes import storage connection.',
        request={
            'application/json': _databricks_volumes_import_storage_schema_with_id,
        },
        responses={200: OpenApiResponse(description='Validation successful')},
        extensions={
            'x-fern-sdk-group-name': ['import_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'validate',
            'x-fern-audiences': ['public'],
        },
    ),
)
class DatabricksVolumesImportStorageValidateAPI(ImportStorageValidateAPI):
    serializer_class = DatabricksVolumesImportStorageSerializer


@method_decorator(
    name='post',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Validate export storage',
        description='Validate a specific Databricks Unity Catalog Volumes export storage connection.',
        request={
            'application/json': _databricks_volumes_export_storage_schema_with_id,
        },
        responses={200: OpenApiResponse(description='Validation successful')},
        extensions={
            'x-fern-sdk-group-name': ['export_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'validate',
            'x-fern-audiences': ['public'],
        },
    ),
)
class DatabricksVolumesExportStorageValidateAPI(ExportStorageValidateAPI):
    serializer_class = DatabricksVolumesExportStorageSerializer


@method_decorator(
    name='get',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Get all export storage',
        description='Get a list of all Databricks Unity Catalog Volumes export storage connections.',
        parameters=[
            OpenApiParameter(
                name='project',
                type=OpenApiTypes.INT,
                location='query',
                description='Project ID',
                required=True,
            ),
        ],
        extensions={
            'x-fern-sdk-group-name': ['export_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'list',
            'x-fern-audiences': ['public'],
        },
    ),
)
@method_decorator(
    name='post',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Create export storage',
        description='Create a new Databricks Unity Catalog Volumes export storage connection to store annotations.',
        request={
            'application/json': _databricks_volumes_export_storage_schema,
        },
        extensions={
            'x-fern-sdk-group-name': ['export_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'create',
            'x-fern-audiences': ['public'],
        },
    ),
)
class DatabricksVolumesExportStorageListAPI(ExportStorageListAPI):
    queryset = DatabricksVolumesExportStorage.objects.all()
    serializer_class = DatabricksVolumesExportStorageSerializer


@method_decorator(
    name='get',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Get export storage',
        description='Get a specific Databricks Unity Catalog Volumes export storage connection.',
        request=None,
        extensions={
            'x-fern-sdk-group-name': ['export_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'get',
            'x-fern-audiences': ['public'],
        },
    ),
)
@method_decorator(
    name='patch',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Update export storage',
        description='Update a specific Databricks Unity Catalog Volumes export storage connection.',
        request={
            'application/json': _databricks_volumes_export_storage_schema,
        },
        extensions={
            'x-fern-sdk-group-name': ['export_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'update',
            'x-fern-audiences': ['public'],
        },
    ),
)
@method_decorator(
    name='delete',
    decorator=extend_schema(
        tags=['Storage: Databricks Unity Catalog'],
        summary='Delete export storage',
        description='Delete a specific Databricks Unity Catalog Volumes export storage connection.',
        request=None,
        extensions={
            'x-fern-sdk-group-name': ['export_storage', 'databricks_volumes'],
            'x-fern-sdk-method-name': 'delete',
            'x-fern-audiences': ['public'],
        },
    ),
)
class DatabricksVolumesExportStorageDetailAPI(ExportStorageDetailAPI):
    queryset = DatabricksVolumesExportStorage.objects.all()
    serializer_class = DatabricksVolumesExportStorageSerializer


class DatabricksVolumesImportStorageFormLayoutAPI(ImportStorageFormLayoutAPI):
    pass


class DatabricksVolumesExportStorageFormLayoutAPI(ExportStorageFormLayoutAPI):
    pass
