from unittest import TestCase

from isitopenaccess.plugins import pmid
from isitopenaccess import models

# some random PMIDs obtained by just doing a search for "test" on the pubmed dataset

PMIDS = [
    "9254694", # example of (real) 7-digit PMID
    "23373100",
    "23373089",
    "23373059",
    "23373049",
    "23373046",
    "23373030"
]

CANONICAL = {
    "9254694" : "pmid:9254694",
    "23373100" : "pmid:23373100",
    "23373089" : "pmid:23373089",
    "23373059" : "pmid:23373059",
    "23373049" : "pmid:23373049",
    "23373046" : "pmid:23373046",
    "23373030" : "pmid:23373030"
}

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
        #- less than 7 and more than 8 digits
        #- random strings (i.e. not just digits)
        
        # some random digits
        bjid = {'id' : 'qp23u4ehjkjewfiuwqr'} # random numbers and digits
        pmid.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        bjid = {'id' : 'qp23u4.10238765.jewfiuwqr'} # has an 8 digit substring in it
            # (therefore also has a 7-digit substring in it)
        pmid.type_detect_verify(bjid)
        assert not bjid.has_key("type")
        
        # less than 7 and more than 8 digits
        bjid = {'id' : '123456'}
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
    
