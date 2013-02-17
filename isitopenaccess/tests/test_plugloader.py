from unittest import TestCase

from isitopenaccess import plugloader, config

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
