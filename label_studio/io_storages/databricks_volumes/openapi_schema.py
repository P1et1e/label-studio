"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""

# Common Databricks Volumes storage schema properties following OpenAPI 3.0 specification
_common_databricks_volumes_storage_schema_properties = {
    'title': {'type': 'string', 'description': 'Storage title', 'maxLength': 2048},
    'description': {'type': 'string', 'description': 'Storage description'},
    'project': {'type': 'integer', 'description': 'Project ID'},
    'databricks_host': {
        'type': 'string',
        'description': 'Databricks workspace URL (e.g. https://dbc-xxx.cloud.databricks.com)',
    },
    'catalog': {'type': 'string', 'description': 'Unity Catalog catalog name'},
    'schema_name': {'type': 'string', 'description': 'Unity Catalog schema name'},
    'volume': {'type': 'string', 'description': 'Unity Catalog volume name'},
    'prefix': {'type': 'string', 'description': 'Path prefix within the volume'},
    'databricks_client_id': {'type': 'string', 'description': 'Databricks Service Principal client ID'},
    'databricks_client_secret': {'type': 'string', 'description': 'Databricks Service Principal OAuth secret'},
}

# Databricks Volumes import storage schema
_databricks_volumes_import_storage_schema = {
    'type': 'object',
    'properties': {
        'regex_filter': {
            'type': 'string',
            'description': 'Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.',
        },
        'use_blob_urls': {
            'type': 'boolean',
            'description': 'Interpret objects as BLOBs and generate URLs. For example, if your volume contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.',
            'default': False,
        },
        'recursive_scan': {
            'type': 'boolean',
            'description': 'Perform recursive scan over the volume content',
            'default': False,
        },
        **_common_databricks_volumes_storage_schema_properties,
    },
    'required': [],
}

# Databricks Volumes import storage schema with ID
_databricks_volumes_import_storage_schema_with_id = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer', 'description': 'Storage ID. If set, storage with specified ID will be updated'},
        **_databricks_volumes_import_storage_schema['properties'],
    },
    'required': [],
}

# Databricks Volumes export storage schema
_databricks_volumes_export_storage_schema = {
    'type': 'object',
    'properties': {
        'can_delete_objects': {'type': 'boolean', 'description': 'Deletion from storage enabled.', 'default': False},
        **_common_databricks_volumes_storage_schema_properties,
    },
    'required': [],
}

# Databricks Volumes export storage schema with ID
_databricks_volumes_export_storage_schema_with_id = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer', 'description': 'Storage ID. If set, storage with specified ID will be updated'},
        **_databricks_volumes_export_storage_schema['properties'],
    },
    'required': [],
}
