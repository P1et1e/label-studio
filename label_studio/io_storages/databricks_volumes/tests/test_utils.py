"""Tests for Databricks Volumes utility functions."""

import io
import unittest
from unittest.mock import MagicMock, patch

from io_storages.databricks_volumes.utils import DatabricksVolumes


class TestGetVolumePath(unittest.TestCase):
    """Test volume path construction."""

    def test_basic_path(self):
        result = DatabricksVolumes.get_volume_path('my_catalog', 'my_schema', 'my_volume')
        assert result == '/Volumes/my_catalog/my_schema/my_volume'

    def test_path_with_prefix(self):
        result = DatabricksVolumes.get_volume_path('cat', 'sch', 'vol', prefix='data/images')
        assert result == '/Volumes/cat/sch/vol/data/images'

    def test_path_with_prefix_trailing_slash(self):
        result = DatabricksVolumes.get_volume_path('cat', 'sch', 'vol', prefix='data/')
        assert result == '/Volumes/cat/sch/vol/data'

    def test_path_with_key(self):
        result = DatabricksVolumes.get_volume_path('cat', 'sch', 'vol', key='file.json')
        assert result == '/Volumes/cat/sch/vol/file.json'

    def test_path_with_prefix_and_key(self):
        result = DatabricksVolumes.get_volume_path('cat', 'sch', 'vol', prefix='data', key='file.json')
        assert result == '/Volumes/cat/sch/vol/data/file.json'

    def test_path_with_nested_key(self):
        result = DatabricksVolumes.get_volume_path('cat', 'sch', 'vol', key='sub/dir/file.json')
        assert result == '/Volumes/cat/sch/vol/sub/dir/file.json'


class TestGetUri(unittest.TestCase):
    """Test URI construction."""

    def test_basic_uri(self):
        result = DatabricksVolumes.get_uri('my_catalog', 'my_schema', 'my_volume', 'file.json')
        assert result == 'uc-volumes://my_catalog.my_schema.my_volume/file.json'

    def test_uri_with_nested_key(self):
        result = DatabricksVolumes.get_uri('cat', 'sch', 'vol', 'sub/dir/file.json')
        assert result == 'uc-volumes://cat.sch.vol/sub/dir/file.json'


class TestGetClient(unittest.TestCase):
    """Test client creation and caching."""

    def setUp(self):
        DatabricksVolumes._client_cache.clear()

    @patch('io_storages.databricks_volumes.utils.WorkspaceClient')
    def test_creates_client(self, mock_ws_class):
        mock_client = MagicMock()
        mock_ws_class.return_value = mock_client

        result = DatabricksVolumes.get_client('https://host.com', 'client_id', 'secret')
        assert result is mock_client
        mock_ws_class.assert_called_once_with(
            host='https://host.com',
            client_id='client_id',
            client_secret='secret',
        )

    @patch('io_storages.databricks_volumes.utils.WorkspaceClient')
    def test_caches_client(self, mock_ws_class):
        mock_client = MagicMock()
        mock_ws_class.return_value = mock_client

        result1 = DatabricksVolumes.get_client('https://host.com', 'cid', 'secret')
        result2 = DatabricksVolumes.get_client('https://host.com', 'cid', 'secret')
        assert result1 is result2
        assert mock_ws_class.call_count == 1

    @patch('io_storages.databricks_volumes.utils.WorkspaceClient')
    def test_different_creds_different_client(self, mock_ws_class):
        DatabricksVolumes.get_client('https://host.com', 'cid1', 'secret1')
        DatabricksVolumes.get_client('https://host.com', 'cid2', 'secret2')
        assert mock_ws_class.call_count == 2


class TestValidateConnection(unittest.TestCase):
    """Test connection validation."""

    def setUp(self):
        DatabricksVolumes._client_cache.clear()

    @patch('io_storages.databricks_volumes.utils.WorkspaceClient')
    def test_validate_connection_success(self, mock_ws_class):
        mock_client = MagicMock()
        mock_ws_class.return_value = mock_client
        mock_client.files.list_directory_contents.return_value = []

        # Should not raise
        DatabricksVolumes.validate_connection(
            'https://host.com', 'cid', 'secret', 'catalog', 'schema', 'volume'
        )
        mock_client.files.list_directory_contents.assert_called_once_with(
            '/Volumes/catalog/schema/volume'
        )

    @patch('io_storages.databricks_volumes.utils.WorkspaceClient')
    def test_validate_connection_with_prefix(self, mock_ws_class):
        mock_client = MagicMock()
        mock_ws_class.return_value = mock_client
        mock_client.files.list_directory_contents.return_value = []

        DatabricksVolumes.validate_connection(
            'https://host.com', 'cid', 'secret', 'catalog', 'schema', 'volume', prefix='data'
        )
        mock_client.files.list_directory_contents.assert_called_once_with(
            '/Volumes/catalog/schema/volume/data'
        )

    @patch('io_storages.databricks_volumes.utils.WorkspaceClient')
    def test_validate_connection_failure(self, mock_ws_class):
        mock_client = MagicMock()
        mock_ws_class.return_value = mock_client
        mock_client.files.list_directory_contents.side_effect = Exception('Access denied')

        with self.assertRaises(Exception):
            DatabricksVolumes.validate_connection(
                'https://host.com', 'cid', 'secret', 'catalog', 'schema', 'volume'
            )


class TestIterFiles(unittest.TestCase):
    """Test file iteration."""

    def _make_entry(self, path, is_directory=False, file_size=100):
        entry = MagicMock()
        entry.path = path
        entry.is_directory = is_directory
        entry.file_size = file_size
        return entry

    def test_iter_files_basic(self):
        mock_client = MagicMock()
        entries = [
            self._make_entry('/Volumes/cat/sch/vol/file1.json'),
            self._make_entry('/Volumes/cat/sch/vol/file2.json'),
        ]
        mock_client.files.list_directory_contents.return_value = entries

        results = list(DatabricksVolumes.iter_files(mock_client, 'cat', 'sch', 'vol'))
        assert len(results) == 2

    def test_iter_files_skips_directories(self):
        mock_client = MagicMock()
        entries = [
            self._make_entry('/Volumes/cat/sch/vol/subdir', is_directory=True),
            self._make_entry('/Volumes/cat/sch/vol/file.json'),
        ]
        mock_client.files.list_directory_contents.return_value = entries

        results = list(DatabricksVolumes.iter_files(mock_client, 'cat', 'sch', 'vol', recursive_scan=False))
        assert len(results) == 1
        assert results[0].path == '/Volumes/cat/sch/vol/file.json'

    def test_iter_files_with_regex_filter(self):
        mock_client = MagicMock()
        entries = [
            self._make_entry('/Volumes/cat/sch/vol/file.json'),
            self._make_entry('/Volumes/cat/sch/vol/file.csv'),
        ]
        mock_client.files.list_directory_contents.return_value = entries

        results = list(DatabricksVolumes.iter_files(
            mock_client, 'cat', 'sch', 'vol', regex_filter='.*\\.json'
        ))
        assert len(results) == 1
        assert results[0].path == '/Volumes/cat/sch/vol/file.json'


class TestReadFile(unittest.TestCase):
    """Test file reading."""

    def test_read_file(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.contents.read.return_value = b'{"data": "test"}'
        mock_client.files.download.return_value = mock_response

        result = DatabricksVolumes.read_file(mock_client, '/Volumes/cat/sch/vol/file.json')
        assert result == b'{"data": "test"}'
        mock_client.files.download.assert_called_once_with('/Volumes/cat/sch/vol/file.json')


class TestUploadFile(unittest.TestCase):
    """Test file upload."""

    def test_upload_file(self):
        mock_client = MagicMock()
        data = b'{"result": "annotation"}'

        DatabricksVolumes.upload_file(mock_client, '/Volumes/cat/sch/vol/output.json', data)
        mock_client.files.upload.assert_called_once()
        call_args = mock_client.files.upload.call_args
        assert call_args[0][0] == '/Volumes/cat/sch/vol/output.json'
        # bytes should be wrapped in BytesIO for the Databricks SDK
        contents = call_args[0][1]
        assert isinstance(contents, io.BytesIO)
        assert contents.read() == data
        assert call_args[1]['overwrite'] is True

    def test_upload_file_bytesio_passthrough(self):
        """BytesIO objects should be passed through without double-wrapping."""
        mock_client = MagicMock()
        data = io.BytesIO(b'already wrapped')

        DatabricksVolumes.upload_file(mock_client, '/Volumes/cat/sch/vol/output.json', data)
        call_args = mock_client.files.upload.call_args
        contents = call_args[0][1]
        assert contents is data


class TestDeleteFile(unittest.TestCase):
    """Test file deletion."""

    def test_delete_file(self):
        mock_client = MagicMock()

        DatabricksVolumes.delete_file(mock_client, '/Volumes/cat/sch/vol/file.json')
        mock_client.files.delete.assert_called_once_with('/Volumes/cat/sch/vol/file.json')
