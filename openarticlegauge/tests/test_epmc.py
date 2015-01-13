from unittest import TestCase

from openarticlegauge.plugins.epmc import EPMCPlugin
from openarticlegauge import models

EPMCS = [
    # These are all valid EPMCs
    "PMC12345",
    "12345",
    "PMC123456",
    "123456",
    "PMC1234567",
    "1234567"
]

CANONICAL = {
    "12345" : "PMC12345",
    "1234567" : "PMC1234567"
}


class MockResponse():
    def __init__(self, status):
        self.status_code = status
        self.text = None
        self.url = None
        
class TestEpmc(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_01_detect_verify_type_real_epmcs(self):
        epmc = EPMCPlugin()
        counter = 0
        for d in EPMCS:
            bjid = {'id' : d}
            record = models.MessageObject(bid=bjid)
            epmc.type_detect_verify(record)
            assert bjid.has_key("type")
            assert bjid["type"] == "epmc"
            counter += 1
        assert counter == len(EPMCS)
        assert counter > 0
    
    def test_02_detect_verify_type_not_epmcs(self):
        #Test the various erroneous EPMC possibilities, which will include:
        #- less than 5 and more than 7 digits
        #- random strings (i.e. not just digits)
        epmc = EPMCPlugin()
        
        # some random digits
        bjid = {'id' : 'qp23u4ehjkjewfiuwqr'} # random numbers and digits
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'qp23u4.1023876.jewfiuwqr'} # has an 7 digit substring in it
            # (therefore also has a 1,2..6-digit substring in it)
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        # less than 5 and more than 7 digits
        bjid = {'id' : ''} # well, less than 1 digit doesn't exist
            # and letters are covered elsewhere...
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")

        bjid = {'id' : '1'}
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")

        bjid = {'id' : '12'}
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")

        bjid = {'id' : '123'}
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")

        bjid = {'id' : '1234'}
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")
        
        bjid = {'id' : '12345678'}
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")
        
    def test_03_detect_verify_type_ignores(self):
        epmc = EPMCPlugin()
        
        bjid = {"id" : "whatever", "type" : "doi"}
        record = models.MessageObject(bid=bjid)
        epmc.type_detect_verify(record)
        assert bjid['type'] == "doi"
        
        bjid = {"key" : "value"}
        record = models.MessageObject(record={"identifier" : bjid})
        epmc.type_detect_verify(record)
        assert not bjid.has_key("type")
    
    def test_04_detect_verify_type_error(self):
        # create an invalid epmc and assert it is a epmc
        epmc = EPMCPlugin()
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "epmc"}
        record = models.MessageObject(bid=bjid)
        with self.assertRaises(models.LookupException):
            epmc.type_detect_verify(record)
            
    def test_05_canonicalise_real(self):
        epmc = EPMCPlugin()
        counter = 0
        for d in CANONICAL.keys():
            bjid = {'id' : d, 'type' : 'epmc'}
            record = models.MessageObject(bid=bjid)
            epmc.canonicalise(record)
            assert bjid.has_key("canonical")
            assert bjid["canonical"] == CANONICAL[d]
            counter += 1
        assert counter == len(CANONICAL.keys())
        assert counter > 0
        
    def test_06_canonicalise_ignore(self):
        epmc = EPMCPlugin()
        bjid = {"id" : "whatever", "type" : "doi"}
        record = models.MessageObject(bid=bjid)
        epmc.canonicalise(record)
        assert not bjid.has_key("canonical")
        
    def test_07_canonicalise_error(self):
        epmc = EPMCPlugin()
        # create an invalid epmc and assert it is a epmc
        bjid = {"id" : "a;lkdsjfjdsajadskja", "type" : "epmc"}
        record = models.MessageObject(bid=bjid)
        with self.assertRaises(models.LookupException):
            epmc.canonicalise(record)
            
        bjid = {"key" : "value"}
        record = models.MessageObject(record={"identifier" : bjid})
        with self.assertRaises(models.LookupException):
            epmc.canonicalise(record)
    
    def test_08_provider_resolve_not_relevant(self):
        epmc = EPMCPlugin()
        record = models.MessageObject()
        
        epmc.detect_provider(record)
        assert len(record.record.keys()) == 0

        record.id = "123"
        record.identifier_type = "doi"
        record.canonical = "doi:123"
        epmc.detect_provider(record)
        assert not "provider" in record.record

        record.identifier_type = "epmc"
        record.canonical = None
        epmc.detect_provider(record)
        assert not "provider" in record.record
        
    def test_09_provider_resolve_doi(self):
        epmc = EPMCPlugin()
        
        record = {"identifier" : {"id" : "1234567", "type" : "epmc", "canonical" : "PMC1234567"}}
        record = models.MessageObject(record=record)
        
        epmc.detect_provider(record)
        
        record = record.record
        assert "provider" in record
        assert "url" in record["provider"]
        assert record['provider']["url"][0] == "http://europepmc.org/articles/PMC1234567", record['provider']['url']
        assert "doi" not in record["provider"]