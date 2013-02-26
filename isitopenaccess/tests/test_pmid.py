from unittest import TestCase

from isitopenaccess.plugins import pmid
from isitopenaccess import models

import os, requests

# some random PMIDs obtained by just doing a search for "test" on the pubmed dataset
# and adding random numbers to the end of http://www.ncbi.nlm.nih.gov/pubmed/<number>
# e.g. http://www.ncbi.nlm.nih.gov/pubmed/1

PMIDS = [
    # These are all real PMIDs
    "1",
    "12",
    "123",
    "1234",
    "12345",
    "123456",
    "9254694",
    "23373100",
    "23373089",
    "23373059",
    "23373049",
    "23373046",
    "23373030"
]

CANONICAL = {
    "1" : "pmid:1",
    "12" : "pmid:12",
    "123" : "pmid:123",
    "1234" : "pmid:1234",
    "12345" : "pmid:12345",
    "123456" : "pmid:123456",
    "9254694" : "pmid:9254694",
    "23373100" : "pmid:23373100",
    "23373089" : "pmid:23373089",
    "23373059" : "pmid:23373059",
    "23373049" : "pmid:23373049",
    "23373046" : "pmid:23373046",
    "23373030" : "pmid:23373030"
}

ENTREZ_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "entrez_pmid_23175652.xml")

class MockResponse():
    def __init__(self, status):
        self.status_code = status
        self.text = None
        self.url = None
        
def get_pmid(url):
    resp = MockResponse(200)
    if url == "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=23175652&retmode=xml":
        with open(ENTREZ_FILE) as f:
            resp.text = f.read()
    elif url == "http://dx.doi.org/10.1128/JB.01321-12":
        resp.url = "http://jb.asm.org/content/195/3/502"
    return resp

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_01_detect_verify_type_real_pmids(self):
        counter = 0
        for d in PMIDS:
            bjid = {'id' : d}
            pmid.type_detect_verify(bjid)
            assert bjid.has_key("type")
            assert bjid["type"] == "pmid"
            counter += 1
        assert counter == len(PMIDS)
        assert counter > 0
    
    def test_02_detect_verify_type_not_pmids(self):
        #Test the various erroneous PMID possibilities, which will include:
        #- less than 1 and more than 8 digits
        #- random strings (i.e. not just digits)
        
        # some random digits
        bjid = {'id' : 'qp23u4ehjkjewfiuwqr'} # random numbers and digits
        pmid.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'qp23u4.10238765.jewfiuwqr'} # has an 8 digit substring in it
            # (therefore also has a 1,2..7-digit substring in it)
        pmid.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        # less than 1 and more than 8 digits
        bjid = {'id' : ''} # well, less than 1 digit doesn't exist
            # and letters are covered elsewhere...
        pmid.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        bjid = {'id' : '123456789'}
        pmid.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
    def test_03_detect_verify_type_ignores(self):
        bjid = {"id" : "whatever", "type" : "doi"}
        pmid.type_detect_verify(bjid)
        assert bjid['type'] == "doi"
        
        bjid = {"key" : "value"}
        pmid.type_detect_verify(bjid)
        assert not bjid.has_key("type")
    
    def test_04_detect_verify_type_error(self):
        # create an invalid pmid and assert it is a pmid
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "pmid"}
        with self.assertRaises(models.LookupException):
            pmid.type_detect_verify(bjid)
            
    def test_05_canonicalise_real(self):
        counter = 0
        for d in CANONICAL.keys():
            bjid = {'id' : d, 'type' : 'pmid'}
            pmid.canonicalise(bjid)
            assert bjid.has_key("canonical")
            assert bjid["canonical"] == CANONICAL[d]
            counter += 1
        assert counter == len(CANONICAL.keys())
        assert counter > 0
        
    def test_06_canonicalise_ignore(self):
        bjid = {"id" : "whatever", "type" : "doi"}
        pmid.canonicalise(bjid)
        assert not bjid.has_key("canonical")
        
    def test_07_canonicalise_error(self):
        # create an invalid pmid and assert it is a pmid
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "pmid"}
        with self.assertRaises(models.LookupException):
            pmid.canonicalise(bjid)
            
        bjid = {"key" : "value"}
        with self.assertRaises(models.LookupException):
            pmid.canonicalise(bjid)
    
    def test_08_provider_resolve_not_relevant(self):
        record = {}
        
        pmid.provider_resolver(record)
        assert len(record.keys()) == 0
        
        record['identifier'] = {}
        pmid.provider_resolver(record)
        assert len(record['identifier'].keys()) == 0
        
        record['identifier']['id'] = "123"
        record['identifier']['type'] = "doi"
        record['identifier']['canonical'] = "doi:123"
        pmid.provider_resolver(record)
        assert not "provider" in record
        
        record['identifier']['type'] = "pmid"
        del record['identifier']['canonical']
        pmid.provider_resolver(record)
        assert not "provider" in record
        
    def test_09_provider_resolve_doi(self):
        old_get = requests.get
        requests.get = get_pmid
        
        record = {"identifier" : {"id" : "23175652", "type" : "pmid", "canonical" : "pmid:23175652"}}
        
        pmid.provider_resolver(record)
        assert "provider" in record
        assert "url" in record["provider"]
        assert record['provider']["url"] == "http://jb.asm.org/content/195/3/502"
        
        requests.get = old_get
    
