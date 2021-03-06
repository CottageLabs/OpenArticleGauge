from unittest import TestCase

from openarticlegauge.plugins.doi import DOIPlugin
from openarticlegauge import models
from openarticlegauge import plugin
from openarticlegauge import util

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

def get_fail(url):
    return MockResponse(404)

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
            record = models.MessageObject(record={"identifier" : bjid})
            doi.type_detect_verify(record)
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
        record = models.MessageObject(record={"identifier" : bjid})
        doi.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'http://dx.doi.org/'}
        record = models.MessageObject(record={"identifier" : bjid})
        doi.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        # try some random strings
        bjid = {'id' : 'qp23u4ehjkjewfiuwqr'}
        record = models.MessageObject(record={"identifier" : bjid})
        doi.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'qp23u410.jewfiuwqr'} # has the 10. substring in it
        record = models.MessageObject(record={"identifier" : bjid})
        doi.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'doi:qp23u4ehjkjewfiuwqr'} # starts with a doi prefix, but isn't one
        record = models.MessageObject(record={"identifier" : bjid})
        doi.type_detect_verify(record)
        assert not bjid.has_key("type")
        
    def test_03_detect_verify_type_ignores(self):
        doi = DOIPlugin()
        
        bjid = {"id" : "whatever", "type" : "pmid"}
        record = models.MessageObject(record={"identifier" : bjid})
        doi.type_detect_verify(record)
        assert bjid['type'] == "pmid"
        
        bjid = {"key" : "value"}
        record = models.MessageObject(record={"identifier" : bjid})
        doi.type_detect_verify(record)
        assert not bjid.has_key("type")
    
    def test_04_detect_verify_type_error(self):
        doi = DOIPlugin()
        
        # create an invalid doi and assert it is a doi
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "doi"}
        record = models.MessageObject(record={"identifier" : bjid})
        with self.assertRaises(models.LookupException):
            doi.type_detect_verify(record)
    
    def test_05_canonicalise_real(self):
        doi = DOIPlugin()
        
        counter = 0
        for d in CANONICAL.keys():
            bjid = {'id' : d, 'type' : 'doi'}
            record = models.MessageObject(record={"identifier" : bjid})
            doi.canonicalise(record)
            assert bjid.has_key("canonical")
            assert bjid["canonical"] == CANONICAL[d]
            counter += 1
        assert counter == len(CANONICAL.keys())
        assert counter > 0
        
    def test_06_canonicalise_ignore(self):
        doi = DOIPlugin()
        
        bjid = {"id" : "whatever", "type" : "pmid"}
        record = models.MessageObject(record={"identifier" : bjid})
        doi.canonicalise(record)
        assert not bjid.has_key("canonical")
        
    def test_07_canonicalise_error(self):
        doi = DOIPlugin()
        
        # create an invalid doi and assert it is a doi
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "doi"}
        record = models.MessageObject(record={"identifier" : bjid})
        with self.assertRaises(models.LookupException):
            doi.canonicalise(record)
            
        bjid = {"key" : "value"}
        record = models.MessageObject(record={"identifier" : bjid})
        with self.assertRaises(models.LookupException):
            doi.canonicalise(record)
    
    def test_08_dereference_not_relevant(self):
        doi = DOIPlugin()
        record = models.MessageObject(record={})
        
        doi.provider_dereference(record)
        assert len(record.record.keys()) == 0

        record.id = "123"
        record.identifier_type = "pmid"
        record.canonical = "pmid:123"
        doi.provider_dereference(record)
        assert not "provider" in record.record

        record.identifier_type = "doi"
        record.canonical = None
        doi.provider_dereference(record)
        assert not "provider" in record.record
    
    def test_09_dereference_no_location(self):
        oldget = util.http_get
        util.http_get = get_no_location
        doi = DOIPlugin()
        
        record = {"identifier" : {"id" : "123", "type" : "doi", "canonical" : "doi:123"}}
        record = models.MessageObject(record=record)
        doi.provider_dereference(record)
        record = record.record
        assert "provider" in record
        assert "url" not in record["provider"]
        assert "doi" in record["provider"]
        assert record["provider"]["doi"] == "doi:123"
        
        util.http_get = oldget
        
    def test_10_dereference_success(self):
        oldget = util.http_get
        util.http_get = get_success
        doi = DOIPlugin()
        
        record = {"identifier" : {"id" : "123", "type" : "doi", "canonical" : "doi:123"}}
        record = models.MessageObject(record=record)
        doi.provider_dereference(record)
        record = record.record
        assert "provider" in record
        assert "url" in record["provider"]
        assert record['provider']['url'][0] == "http://location"
        assert record["provider"]["doi"] == "doi:123"
        
        util.http_get = oldget
        
    def test_11_dereference_success_via_detect_provider(self):
        oldget = util.http_get
        util.http_get = get_success
        doi = DOIPlugin()
        
        record = {"identifier" : {"id" : "123", "type" : "doi", "canonical" : "doi:123"}}
        record = models.MessageObject(record=record)
        doi.detect_provider(record)
        record = record.record
        assert "provider" in record
        assert "url" in record["provider"]
        assert record['provider']['url'][0] == "http://location"
        assert record["provider"]["doi"] == "doi:123"
        
        util.http_get = oldget

    def test_12_dereference_fail(self):
        oldget = util.http_get
        util.http_get = get_fail

        doi = DOIPlugin()
        record = {"identifier" : {"id" : "123", "type" : "doi", "canonical" : "doi:123"}}
        record = models.MessageObject(record=record)
        with self.assertRaises(plugin.PluginException):
            doi.detect_provider(record)

        util.http_get = oldget
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
