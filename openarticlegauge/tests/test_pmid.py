from unittest import TestCase

from openarticlegauge.plugins.pmid import PMIDPlugin
from openarticlegauge import model_exceptions, models

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
NCBI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "ncbi.23175652.html")
NCBI_NO_ICON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "ncbi.1234567.html")

class MockResponse():
    def __init__(self, status):
        self.status_code = status
        self.text = None
        self.url = None
        
def get_doi(url):
    resp = MockResponse(200)
    if url == "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=23175652&retmode=xml":
        with open(ENTREZ_FILE) as f:
            resp.text = f.read()
    elif url == "http://dx.doi.org/10.1128/JB.01321-12":
        resp.url = "http://jb.asm.org/content/195/3/502"
    return resp

def get_icon(url):
    resp = MockResponse(200)
    if url == "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=23175652&retmode=xml":
        resp.text = ""
    elif url == "http://www.ncbi.nlm.nih.gov/pubmed/23175652":
        with open(NCBI_FILE) as f:
            resp.text = f.read()
    return resp

def get_linkout(url):
    resp = MockResponse(200)
    if url == "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=1234567&retmode=xml":
        resp.text = ""
    elif url == "http://www.ncbi.nlm.nih.gov/pubmed/1234567":
        with open(NCBI_NO_ICON_FILE) as f:
            resp.text = f.read()
    return resp

class TestPmid(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_01_detect_verify_type_real_pmids(self):
        pmid = PMIDPlugin()
        counter = 0
        for d in PMIDS:
            bjid = {'id' : d}
            record = models.MessageObject(bid=bjid)
            pmid.type_detect_verify(record)
            assert bjid.has_key("type")
            assert bjid["type"] == "pmid"
            counter += 1
        assert counter == len(PMIDS)
        assert counter > 0
    
    def test_02_detect_verify_type_not_pmids(self):
        #Test the various erroneous PMID possibilities, which will include:
        #- less than 1 and more than 8 digits
        #- random strings (i.e. not just digits)
        pmid = PMIDPlugin()
        
        # some random digits
        bjid = {'id' : 'qp23u4ehjkjewfiuwqr'} # random numbers and digits
        record = models.MessageObject(bid=bjid)
        pmid.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'qp23u4.10238765.jewfiuwqr'} # has an 8 digit substring in it
            # (therefore also has a 1,2..7-digit substring in it)
        record = models.MessageObject(bid=bjid)
        pmid.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        # less than 1 and more than 8 digits
        bjid = {'id' : ''} # well, less than 1 digit doesn't exist
            # and letters are covered elsewhere...
        record = models.MessageObject(bid=bjid)
        pmid.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        bjid = {'id' : '123456789'}
        record = models.MessageObject(bid=bjid)
        pmid.type_detect_verify(record)
        assert not bjid.has_key("type")
        
    def test_03_detect_verify_type_ignores(self):
        pmid = PMIDPlugin()
        
        bjid = {"id" : "whatever", "type" : "doi"}
        record = models.MessageObject(bid=bjid)
        pmid.type_detect_verify(record)
        assert bjid['type'] == "doi"
        
        bjid = {"key" : "value"}
        record = models.MessageObject(record={"identifier" : bjid})
        pmid.type_detect_verify(record)
        assert not bjid.has_key("type")
    
    def test_04_detect_verify_type_error(self):
        # create an invalid pmid and assert it is a pmid
        pmid = PMIDPlugin()
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "pmid"}
        record = models.MessageObject(bid=bjid)
        with self.assertRaises(model_exceptions.LookupException):
            pmid.type_detect_verify(record)
            
    def test_05_canonicalise_real(self):
        pmid = PMIDPlugin()
        counter = 0
        for d in CANONICAL.keys():
            bjid = {'id' : d, 'type' : 'pmid'}
            record = models.MessageObject(bid=bjid)
            pmid.canonicalise(record)
            assert bjid.has_key("canonical")
            assert bjid["canonical"] == CANONICAL[d]
            counter += 1
        assert counter == len(CANONICAL.keys())
        assert counter > 0
        
    def test_06_canonicalise_ignore(self):
        pmid = PMIDPlugin()
        bjid = {"id" : "whatever", "type" : "doi"}
        record = models.MessageObject(bid=bjid)
        pmid.canonicalise(record)
        assert not bjid.has_key("canonical")
        
    def test_07_canonicalise_error(self):
        pmid = PMIDPlugin()
        # create an invalid pmid and assert it is a pmid
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "pmid"}
        record = models.MessageObject(bid=bjid)
        with self.assertRaises(model_exceptions.LookupException):
            pmid.canonicalise(record)
            
        bjid = {"key" : "value"}
        record = models.MessageObject(record={"identifier" : bjid})
        with self.assertRaises(model_exceptions.LookupException):
            pmid.canonicalise(record)
    
    def test_08_provider_resolve_not_relevant(self):
        pmid = PMIDPlugin()
        record = models.MessageObject()
        
        pmid.detect_provider(record)
        assert len(record.record.keys()) == 0
        
        #record['identifier'] = {}
        #pmid.detect_provider(record)
        #assert len(record['identifier'].keys()) == 0
        
        #record['identifier']['id'] = "123"
        #record['identifier']['type'] = "doi"
        #record['identifier']['canonical'] = "doi:123"
        record.id = "123"
        record.identifier_type = "doi"
        record.canonical = "doi:123"
        pmid.detect_provider(record)
        assert not "provider" in record.record
        
        # record['identifier']['type'] = "pmid"
        record.identifier_type = "pmid"
        # del record['identifier']['canonical']
        record.canonical = None
        pmid.detect_provider(record)
        assert not "provider" in record.record
        
    def test_09_provider_resolve_doi(self):
        old_get = requests.get
        requests.get = get_doi
        pmid = PMIDPlugin()
        
        record = {"identifier" : {"id" : "23175652", "type" : "pmid", "canonical" : "pmid:23175652"}}
        record = models.MessageObject(record=record)
        
        pmid.detect_provider(record)
        
        record = record.record
        assert "provider" in record
        assert "url" in record["provider"]
        assert record['provider']["url"][0] == "http://jb.asm.org/content/195/3/502", record['provider']['url']
        assert record["provider"]["doi"] == "doi:10.1128/JB.01321-12"
        
        requests.get = old_get
    
    def test_10_provider_resolve_from_icon(self):
        old_get = requests.get
        requests.get = get_icon
        pmid = PMIDPlugin()
        
        record = {"identifier" : {"id" : "23175652", "type" : "pmid", "canonical" : "pmid:23175652"}}
        record = models.MessageObject(record=record)
        
        pmid.detect_provider(record)
        
        record = record.record
        assert "provider" in record
        assert "url" in record["provider"]
        assert record['provider']["url"][0] == "http://jb.asm.org/cgi/pmidlookup?view=long&pmid=23175652", record['provider']["url"][0]
        
        requests.get = old_get
        
    def test_11_provider_resolve_from_resources(self):
        old_get = requests.get
        requests.get = get_linkout
        pmid = PMIDPlugin()
        
        record = {"identifier" : {"id" : "1234567", "type" : "pmid", "canonical" : "pmid:1234567"}}
        record = models.MessageObject(record=record)
        
        pmid.detect_provider(record)
        
        record = record.record
        assert "provider" in record
        assert "url" in record["provider"]
        assert "http://www.nlm.nih.gov/medlineplus/menopause.html" in record["provider"]["url"], record["provider"]["url"]
        assert "http://toxnet.nlm.nih.gov/cgi-bin/sis/search/r?dbs+hsdb:@term+@rn+50-28-2" in record["provider"]["url"], record["provider"]["url"]
        assert len(record['provider']['url']) == 2
        
        requests.get = old_get
    
