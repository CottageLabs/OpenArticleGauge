from unittest import TestCase
from openarticlegauge import recordmanager

# FIXME: should be removed and replaced with model tests for the MessageObject

class TestRecordManager(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_01_record_provider_url(self):
        record = {}
        recordmanager.record_provider_url(record, "http://hello")
        assert "provider" in record
        assert "url" in record["provider"]
        assert len(record["provider"]["url"]) == 1
        assert record["provider"]["url"][0] == "http://hello"
        
    def test_02_record_provider_urls(self):
        record = {}
        urls = ["http://1", "http://2", "http://3"]
        recordmanager.record_provider_urls(record, urls)
        assert "provider" in record
        assert "url" in record["provider"]
        assert len(record["provider"]["url"]) == 3
        urls.sort()
        record["provider"]["url"].sort()
        assert urls == record["provider"]["url"]
