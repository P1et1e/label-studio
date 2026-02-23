"""Tests for DatabricksVolumesExportStorageLink.get_key().

These tests require Django to be configured because the model import
triggers the app registry.
"""

import os
import unittest
from unittest.mock import MagicMock


def _make_annotation(task_id=42, import_link_key=None, task_data=None):
    """Build a mock annotation with the given task metadata."""
    task = MagicMock()
    task.id = task_id
    task.data = task_data or {}

    if import_link_key is not None:
        link = MagicMock()
        link.key = import_link_key
        task.io_storages_databricksvolumesimportstoragelink = link
    else:
        # No import link — set to None so `if link and link.key` fails
        task.io_storages_databricksvolumesimportstoragelink = None

    annotation = MagicMock()
    annotation.task = task
    return annotation


def _get_key(annotation):
    from io_storages.databricks_volumes.models import DatabricksVolumesExportStorageLink

    return DatabricksVolumesExportStorageLink.get_key(annotation)


class TestExportStorageLinkGetKey(unittest.TestCase):
    """Test export key generation based on source filename."""

    @classmethod
    def setUpClass(cls):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.label_studio')
        import django

        django.setup()

    def test_key_from_import_link(self):
        annotation = _make_annotation(import_link_key='images/photo.jpg')
        assert _get_key(annotation) == 'photo_label.json'

    def test_key_from_import_link_nested_path(self):
        annotation = _make_annotation(import_link_key='sub/dir/document.pdf')
        assert _get_key(annotation) == 'document_label.json'

    def test_key_from_task_data_uri(self):
        data = {'$undefined$': 'uc-volumes://cat.sch.vol/reports/scan.png'}
        annotation = _make_annotation(task_data=data)
        assert _get_key(annotation) == 'scan_label.json'

    def test_key_fallback_to_task_id(self):
        annotation = _make_annotation(task_id=99)
        assert _get_key(annotation) == 'task_99_label.json'

    def test_key_always_json_extension(self):
        annotation = _make_annotation(import_link_key='data.csv')
        assert _get_key(annotation) == 'data_label.json'

    def test_key_from_plain_filename(self):
        annotation = _make_annotation(import_link_key='report.pdf')
        assert _get_key(annotation) == 'report_label.json'
