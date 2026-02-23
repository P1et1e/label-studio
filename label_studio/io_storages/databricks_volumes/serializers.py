"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""

from core.utils.exceptions import extract_message
from io_storages.databricks_volumes.models import DatabricksVolumesExportStorage, DatabricksVolumesImportStorage
from io_storages.serializers import ExportStorageSerializer, ImportStorageSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class DatabricksVolumesImportStorageSerializer(ImportStorageSerializer):
    type = serializers.ReadOnlyField(default='databricks_volumes')
    secure_fields = ['databricks_client_id', 'databricks_client_secret']

    class Meta:
        model = DatabricksVolumesImportStorage
        fields = '__all__'

    def to_representation(self, instance):
        result = super().to_representation(instance)
        for attr in DatabricksVolumesImportStorageSerializer.secure_fields:
            result.pop(attr, None)
        return result

    def validate(self, data):
        data = super().validate(data)
        storage = self.instance
        if storage:
            for key, value in data.items():
                setattr(storage, key, value)
        else:
            if 'id' in self.initial_data:
                storage_object = self.Meta.model.objects.get(id=self.initial_data['id'])
                for attr in DatabricksVolumesImportStorageSerializer.secure_fields:
                    data[attr] = data.get(attr) or getattr(storage_object, attr)
            storage = self.Meta.model(**data)
        try:
            storage.validate_connection()
        except Exception as exc:
            raise ValidationError(extract_message(exc))
        return data


class DatabricksVolumesExportStorageSerializer(ExportStorageSerializer):
    type = serializers.ReadOnlyField(default='databricks_volumes')

    class Meta:
        model = DatabricksVolumesExportStorage
        fields = '__all__'

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result.pop('databricks_client_id', None)
        result.pop('databricks_client_secret', None)
        return result
