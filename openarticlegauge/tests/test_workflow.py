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
from openarticlegauge import config, workflow, models, cache, plugin
import json, os

__version__ = "1.0"

CACHE = {}
ARCHIVE = []

def mock_cache(key, record):
    global CACHE
    CACHE[key] = json.loads(record.json())

def mock_check_cache_general(key):
    global CACHE
    print CACHE
    return models.MessageObject(record=CACHE.get(key))

@classmethod
def mock_store(cls, bibjson):
    global ARCHIVE
    ARCHIVE.append(bibjson)
    
@classmethod
def mock_store_error(cls, bibjson):
    raise Exception("oh dear!")

"""
class mock_doi_type(object):
    def type_detect_verify(self, record):
        if record.id.startswith("10"):
            record.identifier_type = "doi"
            return
        if record.identifier_type == "doi":
            raise models.LookupException("oi")
        
class mock_pmid_type(object):
    def type_detect_verify(self, record):
        if record.id == "12345678":
            record.identifier_type = "pmid"
            
class mock_doi_canon(object):
    def canonicalise(self, record):
        if record.identifier_type == "doi":
            record.canonical = record.identifier_type + ":" + record.id
        
class mock_pmid_canon(object):
    def canonicalise(self, record):
        if record.identifier_type == "pmid":
            record.canonical = record.identifier_type + ":" + record.id
"""

def mock_check_cache(key):
    if key == "doi:10.none": return None
    if key == "doi:10.queued": 
        return models.MessageObject(record={"identifier" : {"id" : "10.queued", "type" : "doi", "canonical": "doi:10.queued"}, "queued" : True})
    if key == "doi:10.bibjson": 
        return models.MessageObject(record={"identifier" : {"id" : "10.bibjson", "type" : "doi", "canonical" : "doi:10.bibjson"}, "bibjson" : {"title" : "fresh"}})
    if key == "doi:10.stale": 
        return models.MessageObject(record={"identifier" : {"id" : "10.stale", "type" : "doi", "canonical" : "doi:10.stale"}, "bibjson" : {"title" : "stale"}})

def mock_queue_cache(key):
    return models.MessageObject(record={"identifier" : {"id" : key}, "queued": True})

def mock_success_cache(key):
    return models.MessageObject(record={"identifier" : {"id" : key}, "bibjson": {"title" : "cached"}})



def mock_is_stale_false(*args, **kwargs): return False

def mock_null_cache(key): return None

@classmethod
def mock_check_archive(cls, key):
    if key == "doi:10.none": return None
    if key == "doi:10.bibjson": return {"title" : "whatever"}
    if key == "doi:10.archived": return {"title" : "archived"}

@classmethod
def mock_null_archive(cls, key): return None

"""
class mock_detect_provider(plugin.Plugin):
    def detect_provider(self, record):
        record.add_provider_url("http://provider")

class mock_no_provider(plugin.Plugin):
    def detect_provider(self, record): 
        pass

class mock_other_detect(plugin.Plugin):
    def detect_provider(self, record):
        record.add_provider_url("http://other")

class mock_detect_provider_error(plugin.Plugin):
    def detect_provider(self, record):
        raise Exception("oh dear!")

class mock_licence_plugin(plugin.Plugin):
    sup = True
    def supports(self, provider):
        return self.sup
    def license_detect(self, record):
        record.record['bibjson'] = {}
        record.record['bibjson']['license'] = [{}]
        record.record['bibjson']['title'] = "mytitle"

class mock_licence_plugin_error(plugin.Plugin):
    def supports(self, provider):
        return True
    def license_detect(self, record):
        raise Exception("oh dear!")

class mock_unknown_licence_plugin(plugin.Plugin):
    __version__ = "1.0"
    _short_name = "test_workflow"
    sup = True
    def supports(self, provider):
        return self.sup
    def license_detect(self, record):
        record.record['bibjson'] = {}
"""

def mock_back_end(record): pass

def mock_is_stale(record):
    return record.record['bibjson']["title"] == "stale"
    
def mock_invalidate(key): pass

def one(): return "one"
def two(): return "two"
def one_two(): return "one_two"

who_to_support = 0
current_support_request = 0
def supports(provider):
    global who_to_support
    global current_support_request
    if current_support_request == who_to_support:
        return True
    current_support_request += 1
    return False

def no_support(provider): return False
def does_support(provider): return True

class TestWorkflow(TestCase):

    def setUp(self):
        # add this test file to the search path for plugins
        #config.module_search_list.append("openarticlegauge.tests")
        #config.module_search_list.append("tests.test_workflow")
        #config.module_search_list.append("openarticlegauge.tests.test_workflow")
        current_support_request = 0
        
        self.old_cache = cache.cache
        self.old_check_cache = cache.check_cache
        
    def tearDown(self):
        global ARCHIVE
        global CACHE
        #for i in range(len(config.module_search_list)):
        #    if config.module_search_list[i] == "tests.test_workflow":
        #        del config.module_search_list[i]
        #        break
        #for i in range(len(config.module_search_list)):
        #    if config.module_search_list[i] == "openarticlegauge.tests.test_workflow":
        #        del config.module_search_list[i]
        #        break
        current_support_request = 0
        del ARCHIVE[:]
        for key in CACHE.keys():
            del CACHE[key]
            
        cache.cache = self.old_cache
        cache.check_cache = self.old_check_cache
            
        
    def test_01_detect_verify_type(self):
        # config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_01")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        # check that we can identify a doi
        record = {"identifier" : {"id" : "10.blah"}}
        record = models.MessageObject(record=record)
        workflow._detect_verify_type(record)
        record = record.record
        assert record["identifier"]["type"] == "doi"
        
        # check we can identify a pmid
        record = {"identifier" : {"id" : "12345678"}}
        record = models.MessageObject(record=record)
        workflow._detect_verify_type(record)
        record = record.record
        assert record["identifier"]["type"] == "pmid"
        
        # check that we can deal with a lookup exception
        record = {"identifier" : {"id" : "123456789", "type" : "doi"}}
        record = models.MessageObject(record=record)
        with self.assertRaises(models.LookupException):
            workflow._detect_verify_type(record)
        
        # check that we can deal with an unidentifiable identifier
        record = {"identifier" : {"id" : "abcd"}}
        record = models.MessageObject(record=record)
        workflow._detect_verify_type(record)
        record = record.record
        assert not record["identifier"].has_key("type")

    def test_02_canonicalise(self):
        # config.canonicalisers = {"doi" : "mock_doi_canon", "pmid" : "mock_pmid_canon"}
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_02")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        # check that we can canonicalise a doi
        record = {"identifier" : {"id" : "10.123456789", "type" : "doi"}}
        record = models.MessageObject(record=record)
        workflow._canonicalise_identifier(record)
        record = record.record
        assert record['identifier']['canonical'] == "doi:10.123456789"
        
        # check that we can canonicalise a pmid
        record = {"identifier" : {"id" : "12345678", "type" : "pmid"}}
        record = models.MessageObject(record=record)
        workflow._canonicalise_identifier(record)
        record = record.record
        assert record['identifier']['canonical'] == "pmid:12345678", record['identifier']['canonical']
        
    def test_03_check_cache(self):
        cache.check_cache = mock_check_cache
        cache.is_stale = mock_is_stale
        cache.invalidate = mock_invalidate
        
        record = {"identifier" : {"id" : "10.none", "type" : "doi", "canonical" : "doi:10.none"}}
        record = models.MessageObject(record=record)
        cache_copy = workflow._check_cache(record)
        assert cache_copy is None
        
        record = {"identifier" : {"id" : "10.queued", "type" : "doi", "canonical" : "doi:10.queued"}}
        record = models.MessageObject(record=record)
        cache_copy = workflow._check_cache(record)
        assert cache_copy.record['queued']
        
        record = {"identifier" : {"id" : "10.bibjson", "type" : "doi", "canonical" : "doi:10.bibjson"}}
        record = models.MessageObject(record=record)
        cache_copy = workflow._check_cache(record)
        assert cache_copy.record.has_key("bibjson")
        assert cache_copy.record["bibjson"]["title"] == "fresh"
        
        record = {"identifier" : {"id" : "10.stale", "type" : "doi", "canonical" : "doi:10.stale"}}
        record = models.MessageObject(record=record)
        cache_copy = workflow._check_cache(record)
        assert cache_copy is None
        
    def test_04_check_archive(self):
        models.Record.check_archive = mock_check_archive
        
        record = {"identifier" : {"id" : "10.none", "type" : "doi", "canonical" : "doi:10.none"}}
        record = models.MessageObject(record=record)
        archive_copy = workflow._check_archive(record)
        assert archive_copy is None
        
        old_is_stale = workflow._is_stale
        workflow._is_stale = mock_is_stale_false
        
        record = {"identifier" : {"id" : "10.bibjson", "type" : "doi", "canonical" : "doi:10.bibjson"}}
        record = models.MessageObject(record=record)
        archive_copy = workflow._check_archive(record)
        workflow._is_stale = old_is_stale
        
        assert archive_copy.has_key("title")
    
    def test_05_cache_success(self):
        ids = [{"id" : "10.cached"}]
        
        # set up the mocks for the first test
        #config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        #config.canonicalisers = {"doi" : "mock_doi_canon", "pmid" : "mock_pmid_canon"}
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_05")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        cache.check_cache = mock_queue_cache
        
        # first do a lookup on a queued version
        rs = workflow.lookup(ids)
        assert len(rs.processing) == 1
        result = rs.processing[0]
        assert result['identifier']['id'] == "10.cached"
        assert result['identifier']['type'] == "doi"
        assert result['identifier']['canonical'] == "doi:10.cached"
        
        # now update the cache mock for the appropriate result
        cache.check_cache = mock_success_cache
        old_is_stale = workflow._is_stale
        workflow._is_stale = mock_is_stale_false
        
        # now the same lookup on a properly cached version
        ids = [{"id" : "10.cached"}]
        rs = workflow.lookup(ids)
        workflow._is_stale = old_is_stale
        
        assert len(rs.results) == 1
        result = rs.results[0]
        assert result['identifier'][0]['id'] == "10.cached"
        assert result['identifier'][0]['type'] == "doi"
        assert result['identifier'][0]['canonical'] == "doi:10.cached", result
        assert result['title'] == "cached"
    
    def test_06_cache_prior_error(self):
        # test to make sure that a prior error causes a lookup error
        global CACHE
        CACHE["doi:10.cached"] = {"error" : "prior error"}
        cache.check_cache = mock_check_cache_general
        
        ids = [{"id" : "10.cached"}]
        rs = workflow.lookup(ids)
        assert len(rs.errors) == 1
    
    def test_07_archive_success(self):
        ids = [{"id" : "10.archived"}]
        
        # set up the mocks for the first test
        #config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        #config.canonicalisers = {"doi" : "mock_doi_canon", "pmid" : "mock_pmid_canon"}
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_07")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        cache.check_cache = mock_null_cache
        models.Record.check_archive = mock_check_archive
        old_is_stale = workflow._is_stale
        workflow._is_stale = mock_is_stale_false
        
        # do a lookup for an archived version
        rs = workflow.lookup(ids)
        workflow._is_stale = old_is_stale
        
        assert len(rs.results) == 1
        result = rs.results[0]
        assert result['identifier'][0]['id'] == "10.archived"
        assert result['identifier'][0]['type'] == "doi"
        assert result['identifier'][0]['canonical'] == "doi:10.archived", result
        assert result['title'] == "archived"
        
    def test_08_lookup_error(self):
        ids = [{"id" : "12345", "type" : "doi"}]
        # config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_08")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        rs = workflow.lookup(ids)
        assert len(rs.errors) == 1
        result = rs.errors[0]
        assert result['identifier']['id'] == "12345"
        assert result['identifier']['type'] == "doi"
        assert result.has_key("error")
    
    def test_09_detect_provider(self):
        record = {"identifier" : {"id" : "12345"}}
        workflow.detect_provider(record)
        
        # the record should not have changed
        assert not record.has_key('provider')
        
        record['identifier']['type'] = "unknown"
        workflow.detect_provider(record)
        
        # the record should not have changed
        assert not "provider" in record
        
        # check that a plugin is applied
        # config.provider_detection = {"doi" : ["mock_detect_provider"]}
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_09_1")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        record['identifier']['type'] = "doi"
        workflow.detect_provider(record)
        assert "provider" in record, record
        assert "url" in record['provider']
        assert record["provider"]["url"][0] == "http://provider"
        
        # now check that the chain continues all the way to the end
        # config.provider_detection = {"doi" : ["mock_no_provider", "mock_other_detect", "mock_detect_provider"]}
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_09_2")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        del record['provider']
        workflow.detect_provider(record)
        assert "provider" in record
        assert "url" in record['provider']
        assert "http://provider" in record["provider"]["url"]
    
    def test_10_detect_provider_errors(self):
        # Identifier type is none
        record = {"identifier" : {"id" : "12345"}}
        workflow.detect_provider(record)
        assert "error" in record
        
        # detect provider fails
        #config.provider_detection = {"doi" : ["mock_detect_provider_error"]}
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_10")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        del record["error"]
        record['identifier']['type'] = "doi"
        workflow.detect_provider(record)
        assert "error" in record
        
        # detect provider fails and message object corrupt
        # config.provider_detection = {"doi" : ["mock_detect_provider_error"]}
        ret = workflow.detect_provider("whatever")
        assert "error" in ret
    
    def test_11_provider_licence(self):
        # config.license_detection = ["mock_licence_plugin"]
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_11_1")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        # first check that no provider results in no change
        record = {}
        workflow.provider_licence(record)
        assert not record.has_key("bibjson")
        
        # now check there's no change if there's no plugin
        # mock_licence_plugin.sup = False
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_11_2")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        record = models.MessageObject(record=record)
        record = record.record
        assert not record.has_key("bibjson")
        
        # check that it works when it's right
        # mock_licence_plugin.sup = True
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_11_1")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        record['provider'] = {"url" : ["testprovider"]}
        workflow.provider_licence(record)
        
        assert record.has_key("bibjson")
        assert record['bibjson'].has_key("license") # american spelling
        assert len(record['bibjson']['license']) == 1
        
    def test_12_provider_unknown_licence(self):
        # config.license_detection = ["mock_unknown_licence_plugin"]
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_12")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        # check that it works when it's right
        record = {}
        record['provider'] = {"url" : ["testprovider"]}
        workflow.provider_licence(record)
        
        # mock_unknown_plugin runs but does not provide us with a licence,
        # but nonetheless, we expect an unknown licence to exist
        assert record.has_key("bibjson")
        assert record['bibjson'].has_key("license") # american spelling
        assert len(record['bibjson']['license']) == 1
        licence = record['bibjson']['license'][0]
        assert licence['url'] == config.unknown_url, (licence['url'], config.unknown_url)
        assert licence["type"] == "failed-to-obtain-license"
        assert licence['provenance']['handler'] == "test_workflow", licence['provenance']['handler']
        assert licence['provenance']['handler_version'] == "1.0", licence['provenance']['handler_version']
    
    def test_13_provider_licence_error(self):
        # config.license_detection = ["mock_licence_plugin"]
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_13_1")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        # no provider
        record = {}
        ret = workflow.provider_licence(record)
        print ret
        assert "error" in ret
        
        # no plugin to handle provider
        # config.license_detection = []
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_13_2")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        if "error" in record: del record["error"]
        record['provider'] = {"url" : ["testprovider"]}
        ret = workflow.provider_licence(record)
        assert "error" in ret
        
        # some error in license detect
        # config.license_detection = ["mock_licence_plugin_error"]
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_13_3")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        if "error" in record: del record["error"]
        ret = workflow.provider_licence(record)
        assert "error" in ret
        
        # some error in licence detect and record corrupt
        # config.license_detection = ["mock_licence_plugin_error"]
        ret = workflow.detect_provider("whatever")
        assert "error" in ret
    
    def test_14_check_cache_update_on_queued(self):
        global CACHE
        ids = [{"id" : "10.queued"}]
        
        # set up the configuration so that the type and canonical form are created
        # but no copy of the id is found in the cache or archive
        #config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        #config.canonicalisers = {"doi" : "mock_doi_canon", "pmid" : "mock_pmid_canon"}
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_14")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        cache.check_cache = mock_null_cache
        models.Record.check_archive = mock_null_archive
        
        # mock out the cache method to allow us to record
        # calls to it
        cache.cache = mock_cache
        
        # mock out the _start_back_end so that we don't actually start the
        # back end
        old_back_end = workflow._start_back_end
        workflow._start_back_end = mock_back_end
        
        # do the lookup
        rs = workflow.lookup(ids)
        
        # assert that the result is in the appropriate bit of the response
        assert len(rs.processing) == 1
        result = rs.processing[0]
        assert result['identifier']['id'] == "10.queued"
        
        # now check our cache and make sure that the item got cached
        # correctly
        assert CACHE.has_key("doi:10.queued")
        assert CACHE["doi:10.queued"]['queued'], CACHE
        
        # reset the test cache and reinstate the old back-end
        del CACHE["doi:10.queued"]
        workflow._start_back_end = old_back_end
    
    def test_15_store(self):
        global CACHE
        global ARCHIVE
        
        cache.cache = mock_cache
        models.Record.store = mock_store
        
        # first check that we get the right behaviour if no licence is provided
        record = {'identifier' : {"id" : "10.1", "type" : "doi", "canonical" : "doi:10.1"}, "queued" : True}
        workflow.store_results(record)
        
        assert CACHE.has_key("doi:10.1")
        assert len(ARCHIVE) == 1
        assert not record.get("queued", False)
        assert "bibjson" in record
        assert "license" in record['bibjson']
        assert record['bibjson']['license'][0]['type'] == "failed-to-obtain-license"
        assert record["bibjson"]["license"][0]["provenance"]["handler"] == "oag"
        assert record["bibjson"]["license"][0]["provenance"]["handler_version"] == "0.0"
        assert "identifier" in record["bibjson"]
        
        del CACHE['doi:10.1']
        del ARCHIVE[0]
        
        # now provide a bibjson record with a licence
        record["bibjson"] = {
            "title" : "mytitle",
            "license" : [{
                "url" : "http://license"   
            }]
        }
        record["queued"] = True
        workflow.store_results(record)
        
        assert CACHE.has_key("doi:10.1")
        assert not CACHE["doi:10.1"].get("queued", False)
        assert len(ARCHIVE) == 1
        assert ARCHIVE[0]["title"] == "mytitle"
        assert not record.get("queued", False)
        assert "identifier" in record['bibjson']
        
        del CACHE['doi:10.1']
        del ARCHIVE[0]
    
    def test_16_store_error(self):
        global CACHE
        global ARCHIVE
        
        cache.cache = mock_cache
        models.Record.store = mock_store
        
        # no canonical identifier
        record = {}
        ret = workflow.store_results(record)
        assert "error" in ret
        
        # pre-existing error
        record = {'identifier' : {"id" : "10.1", "type" : "doi", "canonical" : "doi:10.1"}, "queued" : True, "error" : "oops"}
        ret = workflow.store_results(record)
        
        assert "error" in ret
        assert CACHE.has_key("doi:10.1")
        assert len(ARCHIVE) == 0
        assert not record.get("queued", False)
        assert "bibjson" in record
        assert "license" in record['bibjson']
        assert record['bibjson']['license'][0]['type'] == "failed-to-obtain-license"
        assert "identifier" in record["bibjson"]
        
        del CACHE['doi:10.1']
        
        models.Record.store = mock_store_error
        
        # realistic looking object
        record["bibjson"] = {
            "title" : "mytitle",
            "license" : [{
                "url" : "http://license"   
            }]
        }
        record["queued"] = True
        if "error" in record: del record["error"]
        
        ret = workflow.store_results(record)
        
        assert len(CACHE) == 0, CACHE
        assert len(ARCHIVE) == 0, ARCHIVE
        assert "error" in ret
    
    def test_17_chain(self):
        global CACHE
        global ARCHIVE
        
        record = {'identifier' : {"id" : "10.1", "type" : "doi", "canonical" : "doi:10.1"}, "queued" : True}
        
        #config.provider_detection = {"doi" : ["mock_detect_provider"]}
        #config.license_detection = ["mock_licence_plugin"]
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_workflow", "test_17")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        
        cache.cache = mock_cache
        models.Record.store = mock_store
        
        # run the chain synchronously
        record = workflow.detect_provider(record)
        record = workflow.provider_licence(record)
        record = workflow.store_results(record)
        
        assert "provider" in record
        assert record["provider"]["url"][0] == "http://provider"
        
        assert record.has_key("bibjson")
        assert record['bibjson'].has_key("license")
        
        assert CACHE.has_key("doi:10.1")
        assert not CACHE["doi:10.1"].get("queued", False)
        assert len(ARCHIVE) == 1, len(ARCHIVE)
        assert ARCHIVE[0]["title"] == "mytitle"
        
        del CACHE['doi:10.1']
        del ARCHIVE[0]
        
        
        
        
        
        
        
        
        
        
        
        
        
