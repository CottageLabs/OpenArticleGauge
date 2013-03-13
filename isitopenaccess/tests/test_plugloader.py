from unittest import TestCase

from isitopenaccess import plugloader, config

__version__ = "1.0"

def sibling(provider):
    return "sibling"

def patch():
    return "patched"

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_01_load_monkey_patch(self):
        call = plugloader.load("tests.test_plugloader.patch")
        assert call is not None
        res = call()
        assert res == "patched"
        
    def test_02_load_none(self):
        # shouldn't find the test_plugloader module in this context, so 
        # call will fail
        call = plugloader.load("test_plugloader.patch")
        assert call is None
    
    def test_03_load_error(self):
        # an attempt to load a non existant callable from an
        # existing module
        call = plugloader.load("tests.test_plugloader.nothing")
        assert call is None
    
    def test_04_with_search(self):
        old_search_list = config.module_search_list
        config.module_search_list = ["isitopenaccess.tests"]
        
        call = plugloader.load("test_plugloader.patch")
        assert call is not None
        res = call()
        assert res == "patched"
        
        config.module_search_list = old_search_list
    """
    def test_05_load_sibling(self):
        sib = plugloader.load_sibling("tests.test_plugloader.patch", "sibling")
        assert sib is not None
        res = sib({})
        assert res == "sibling"
        
    def test_06_load_no_sibling(self):
        sib = plugloader.load_sibling("tests.test_plugloader.patch", "whatever")
        assert sib is None
        
    def test_07_load_sibling_with_search(self):
        old_search_list = config.module_search_list
        config.module_search_list = ["isitopenaccess.tests"]
        
        sib = plugloader.load_sibling("test_plugloader.patch", "sibling")
        assert sib is not None
        res = sib({})
        assert res == "sibling"
        
        config.module_search_list = old_search_list
        
    def test_08_get_info(self):
        old_search_list = config.module_search_list
        config.module_search_list = ["isitopenaccess.tests"]
        
        name, version = plugloader.get_info("test_plugloader.patch")
        assert name == "test_plugloader", name
        assert version == "1.0", version
        
        config.module_search_list = old_search_list
    """
    
    def test_09_load_class(self):
        doi_class = plugloader.load("isitopenaccess.plugins.doi.DOIPlugin")
        doi = doi_class()
