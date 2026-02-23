"""Tests for uc-volumes:// URI resolution and parsing."""

import unittest

from io_storages.utils import get_uri_via_regex, parse_bucket_uri


class MockStorage:
    url_scheme = 'uc-volumes'


class TestUcVolumesUriRegex(unittest.TestCase):
    """Test that uc-volumes:// URIs are parsed correctly by get_uri_via_regex."""

    def test_direct_uri(self):
        uri, scheme = get_uri_via_regex('uc-volumes://cat.sch.vol/path/file.json')
        assert uri == 'uc-volumes://cat.sch.vol/path/file.json'
        assert scheme == 'uc-volumes'

    def test_uri_in_quotes(self):
        data = '"uc-volumes://cat.sch.vol/images/photo.jpg"'
        uri, scheme = get_uri_via_regex(data)
        assert uri == 'uc-volumes://cat.sch.vol/images/photo.jpg'
        assert scheme == 'uc-volumes'

    def test_uri_not_matching(self):
        uri, scheme = get_uri_via_regex('s3://bucket/key')
        assert scheme == 's3'

    def test_no_uri(self):
        uri, scheme = get_uri_via_regex('just some text')
        assert uri is None
        assert scheme is None


class TestParseBucketUri(unittest.TestCase):
    """Test parse_bucket_uri with uc-volumes scheme."""

    def test_parse_uc_volumes_uri(self):
        storage = MockStorage()
        result = parse_bucket_uri('uc-volumes://my_cat.my_sch.my_vol/path/to/file.json', storage)
        assert result is not None
        assert result.bucket == 'my_cat.my_sch.my_vol'
        assert result.path == 'path/to/file.json'
        assert result.scheme == 'uc-volumes'

    def test_parse_empty_value(self):
        storage = MockStorage()
        result = parse_bucket_uri('', storage)
        assert result is None

    def test_parse_none_value(self):
        storage = MockStorage()
        result = parse_bucket_uri(None, storage)
        assert result is None

    def test_parse_wrong_scheme(self):
        storage = MockStorage()
        result = parse_bucket_uri('s3://bucket/key', storage)
        assert result is None
