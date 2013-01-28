"""
This set of test cases ensures that the workflow is behaving itself.  

It tests that the mappings from workflow stages to plugins is working.  

It DOES NOT test the plugins themselves.  Any comments which say 
"check that we can identify a doi" or similar mean "check that the 
plugin and workflow framework support the identification of the doi".

All plugin work is done with mock functions defined below.

There are other tests for working on specific plugins.
"""

from unittest import TestCase
import config, workflow, models, cache, archive

def mock_doi_type(bibjson_identifier):
    if bibjson_identifier["id"].startswith("10"):
        bibjson_identifier["type"] = "doi"
        return
    if bibjson_identifier.get("type") == "doi":
        raise models.LookupException("oi")

def mock_pmid_type(bibjson_identifier):
    if bibjson_identifier["id"] == "12345678":
        bibjson_identifier["type"] = "pmid"
        
def mock_doi_canon(record):
    if record['identifier']['type'] == 'doi':
        record['canonical'] = record['identifier']['type'] + ":" + record['identifier']['id']
    
def mock_pmid_canon(record):
    if record['identifier']['type'] == 'pmid':
        record['canonical'] = record['identifier']['type'] + ":" + record['identifier']['id']

def mock_check_cache(key):
    if key == "doi:10.none": return None
    if key == "doi:10.queued": return {"identifier" : {"id" : "10.queued", "type" : "doi"}, "canonical" : "doi:10.queued", "queued" : True}
    if key == "doi:10.bibjson": return {"identifier" : {"id" : "10.bibjson", "type" : "doi"}, "canonical" : "doi:10.bibjson", "bibjson" : {}}

def mock_check_archive(key):
    if key == "doi:10.none": return None
    if key == "doi:10.bibjson": return {"title" : "whatever"}
    
class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_01_detect_verify_type(self):
        config.type_detection = [mock_doi_type, mock_pmid_type]
        
        # check that we can identify a doi
        record = {"identifier" : {"id" : "10.blah"}}
        workflow._detect_verify_type(record)
        assert record["identifier"]["type"] == "doi"
        
        # check we can identify a pmid
        record = {"identifier" : {"id" : "12345678"}}
        workflow._detect_verify_type(record)
        assert record["identifier"]["type"] == "pmid"
        
        # check that we can deal with a lookup exception
        record = {"identifier" : {"id" : "123456789", "type" : "doi"}}
        with self.assertRaises(models.LookupException):
            workflow._detect_verify_type(record)
        
        # check that we can deal with an unidentifiable identifier
        record = {"identifier" : {"id" : "abcd"}}
        workflow._detect_verify_type(record)
        assert not record["identifier"].has_key("type")

    def test_02_canonicalise(self):
        config.canonicalisers = {"doi" : mock_doi_canon, "pmid" : mock_pmid_canon}
        
        # check that we can canonicalise a doi
        record = {"identifier" : {"id" : "10.123456789", "type" : "doi"}}
        workflow._canonicalise_identifier(record)
        assert record['canonical'] == "doi:10.123456789"
        
        # check that we can canonicalise a pmid
        record = {"identifier" : {"id" : "12345678", "type" : "pmid"}}
        workflow._canonicalise_identifier(record)
        assert record['canonical'] == "pmid:12345678", record['canonical']
        
    def test_03_check_cache(self):
        cache.check_cache = mock_check_cache
        
        record = {"identifier" : {"id" : "10.none", "type" : "doi"}, "canonical" : "doi:10.none"}
        cache_copy = workflow._check_cache(record)
        assert cache_copy is None
        
        record = {"identifier" : {"id" : "10.queued", "type" : "doi"}, "canonical" : "doi:10.queued"}
        cache_copy = workflow._check_cache(record)
        assert cache_copy['queued']
        
        record = {"identifier" : {"id" : "10.bibjson", "type" : "doi"}, "canonical" : "doi:10.bibjson"}
        cache_copy = workflow._check_cache(record)
        assert cache_copy.has_key("bibjson")
        
    def test_04_check_archive(self):
        archive.check_archive = mock_check_archive
        
        record = {"identifier" : {"id" : "10.none", "type" : "doi"}, "canonical" : "doi:10.none"}
        archive_copy = workflow._check_archive(record)
        assert archive_copy is None
        
        record = {"identifier" : {"id" : "10.bibjson", "type" : "doi"}, "canonical" : "doi:10.bibjson"}
        archive_copy = workflow._check_archive(record)
        assert archive_copy.has_key("title")
