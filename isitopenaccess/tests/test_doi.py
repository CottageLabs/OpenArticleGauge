from unittest import TestCase

from isitopenaccess.plugins.doi import DOIPlugin
from isitopenaccess import model_exceptions
import requests

# a bunch of random DOIs obtained from CrossRef Labs: curl http://random.labs.crossref.org/dois
# and then augmented with some semi-random prefixes
DOIS = [
    "doi:10.1111/j.0954-6820.1964.tb06335.x",
    "info:doi:10.1021/jm00376a026",
    "http://dx.doi.org/10.1016/j.jsg.2005.01.012",
    "dx.doi.org/10.1002/etc.5620210119",
    "http://hdl.handle.net/10.2177/jsci.8.374",
    "hdl.handle.net/10.1136/bmj.1.2822.189",
    "doi:10.1038/npp.2010.20",
    "info:doi:10.1016/0003-9969(81)90025-X",
    "http://dx.doi.org/10.1016/S0022-5347(08)61457-3",
    "dx.doi.org/10.1017/S0067237800002939",
    "http://hdl.handle.net/10.1016/S0021-9517(02)00048-9",
    "hdl.handle.net/10.1017/S0022377806005071",
    "doi:10.1007/BF02433115",
    "info:doi:10.4271/800132",
    "http://dx.doi.org/10.1111/j.1601-5037.2010.00467.x",
    "dx.doi.org/10.1016/S0098-1354(99)80158-6",
    "http://hdl.handle.net/10.1006/exeh.1999.0718",
    "hdl.handle.net/10.2307/1321609",
    "doi:10.1101/pdb.caut2730",
    "info:doi:10.1021/jo01080a021"
]

CANONICAL = {
    "doi:10.1111/j.0954-6820.1964.tb06335.x" : "doi:10.1111/j.0954-6820.1964.tb06335.x",
    "info:doi:10.1021/jm00376a026" : "doi:10.1021/jm00376a026",
    "http://dx.doi.org/10.1016/j.jsg.2005.01.012" : "doi:10.1016/j.jsg.2005.01.012",
    "dx.doi.org/10.1002/etc.5620210119" : "doi:10.1002/etc.5620210119",
    "http://hdl.handle.net/10.2177/jsci.8.374" : "doi:10.2177/jsci.8.374",
    "hdl.handle.net/10.1136/bmj.1.2822.189" : "doi:10.1136/bmj.1.2822.189"
}

class MockResponse():
    def __init__(self, status):
        self.status_code = status
        self.headers = {}
        self.url = None

def get_no_location(url):
    return MockResponse(200)

def get_success(url):
    r = MockResponse(200)
    r.url = "http://location"
    return r

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_01_detect_verify_type_real_dois(self):
        doi = DOIPlugin()
        counter = 0
        for d in DOIS:
            bjid = {'id' : d}
            doi.type_detect_verify(bjid)
            assert bjid.has_key("type")
            assert bjid["type"] == "doi"
            counter += 1
        assert counter == len(DOIS)
        assert counter > 0
    
    def test_02_detect_verify_type_not_dois(self):
        #Test the various erroneous DOI possibilities, which will include:
        #- prefixes without dois attached
        #- random strings
        doi = DOIPlugin()
        
        # try some prefixes
        bjid = {'id' : 'doi:'}
        doi.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'http://dx.doi.org/'}
        doi.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        # try some random strings
        bjid = {'id' : 'qp23u4ehjkjewfiuwqr'}
        doi.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'qp23u410.jewfiuwqr'} # has the 10. substring in it
        doi.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'doi:qp23u4ehjkjewfiuwqr'} # starts with a doi prefix, but isn't one
        doi.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
    def test_03_detect_verify_type_ignores(self):
        doi = DOIPlugin()
        
        bjid = {"id" : "whatever", "type" : "pmid"}
        doi.type_detect_verify(bjid)
        assert bjid['type'] == "pmid"
        
        bjid = {"key" : "value"}
        doi.type_detect_verify(bjid)
        assert not bjid.has_key("type")
    
    def test_04_detect_verify_type_error(self):
        doi = DOIPlugin()
        
        # create an invalid doi and assert it is a doi
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "doi"}
        with self.assertRaises(model_exceptions.LookupException):
            doi.type_detect_verify(bjid)
    
    def test_05_canonicalise_real(self):
        doi = DOIPlugin()
        
        counter = 0
        for d in CANONICAL.keys():
            bjid = {'id' : d, 'type' : 'doi'}
            doi.canonicalise(bjid)
            assert bjid.has_key("canonical")
            assert bjid["canonical"] == CANONICAL[d]
            counter += 1
        assert counter == len(CANONICAL.keys())
        assert counter > 0
        
    def test_06_canonicalise_ignore(self):
        doi = DOIPlugin()
        
        bjid = {"id" : "whatever", "type" : "pmid"}
        doi.canonicalise(bjid)
        assert not bjid.has_key("canonical")
        
    def test_07_canonicalise_error(self):
        doi = DOIPlugin()
        
        # create an invalid doi and assert it is a doi
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "doi"}
        with self.assertRaises(model_exceptions.LookupException):
            doi.canonicalise(bjid)
            
        bjid = {"key" : "value"}
        with self.assertRaises(model_exceptions.LookupException):
            doi.canonicalise(bjid)
    
    def test_08_dereference_not_relevant(self):
        doi = DOIPlugin()
        record = {}
        
        doi.provider_dereference(record)
        assert len(record.keys()) == 0
        
        record['identifier'] = {}
        doi.provider_dereference(record)
        assert len(record['identifier'].keys()) == 0
        
        record['identifier']['id'] = "123"
        record['identifier']['type'] = "pmid"
        record['identifier']['canonical'] = "pmid:123"
        doi.provider_dereference(record)
        assert not "provider" in record
        
        record['identifier']['type'] = "doi"
        del record['identifier']['canonical']
        doi.provider_dereference(record)
        assert not "provider" in record
    
    def test_09_dereference_no_location(self):
        oldget = requests.get
        requests.get = get_no_location
        doi = DOIPlugin()
        
        record = {"identifier" : {"id" : "123", "type" : "doi", "canonical" : "doi:123"}}
        doi.provider_dereference(record)
        assert "provider" in record
        assert "url" not in record["provider"]
        assert "doi" in record["provider"]
        assert record["provider"]["doi"] == "doi:123"
        
        requests.get = oldget
        
    def test_10_dereference_success(self):
        oldget = requests.get
        requests.get = get_success
        doi = DOIPlugin()
        
        record = {"identifier" : {"id" : "123", "type" : "doi", "canonical" : "doi:123"}}
        doi.provider_dereference(record)
        assert "provider" in record
        assert "url" in record["provider"]
        assert record['provider']['url'][0] == "http://location"
        assert record["provider"]["doi"] == "doi:123"
        
        requests.get = oldget
        
    def test_11_dereference_success_via_detect_provider(self):
        oldget = requests.get
        requests.get = get_success
        doi = DOIPlugin()
        
        record = {"identifier" : {"id" : "123", "type" : "doi", "canonical" : "doi:123"}}
        doi.detect_provider(record)
        assert "provider" in record
        assert "url" in record["provider"]
        assert record['provider']['url'][0] == "http://location"
        assert record["provider"]["doi"] == "doi:123"
        
        requests.get = oldget
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
