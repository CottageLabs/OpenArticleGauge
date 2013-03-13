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
from isitopenaccess import config, workflow, models, cache, archive, plugin

__version__ = "1.0"

CACHE = {}
ARCHIVE = []

def mock_cache(key, obj):
    global CACHE
    CACHE[key] = obj

@classmethod
def mock_store(cls, bibjson):
    global ARCHIVE
    ARCHIVE.append(bibjson)

class mock_doi_type(object):
    def type_detect_verify(self, bibjson_identifier):
        if bibjson_identifier["id"].startswith("10"):
            bibjson_identifier["type"] = "doi"
            return
        if bibjson_identifier.get("type") == "doi":
            raise models.LookupException("oi")

class mock_pmid_type(object):
    def type_detect_verify(self, bibjson_identifier):
        if bibjson_identifier["id"] == "12345678":
            bibjson_identifier["type"] = "pmid"
        
class mock_doi_canon(object):
    def canonicalise(self, bibjson_identifier):
        if bibjson_identifier['type'] == 'doi':
            bibjson_identifier['canonical'] = bibjson_identifier['type'] + ":" + bibjson_identifier['id']
        
class mock_pmid_canon(object):
    def canonicalise(self, bibjson_identifier):
        if bibjson_identifier['type'] == 'pmid':
            bibjson_identifier['canonical'] = bibjson_identifier['type'] + ":" + bibjson_identifier['id']

def mock_check_cache(key):
    if key == "doi:10.none": return None
    if key == "doi:10.queued": return {"identifier" : {"id" : "10.queued", "type" : "doi", "canonical": "doi:10.queued"}, "queued" : True}
    if key == "doi:10.bibjson": return {"identifier" : {"id" : "10.bibjson", "type" : "doi", "canonical" : "doi:10.bibjson"}, "bibjson" : {"title" : "fresh"}}
    if key == "doi:10.stale": return {"identifier" : {"id" : "10.stale", "type" : "doi", "canonical" : "doi:10.stale"}, "bibjson" : {"title" : "stale"}}

def mock_queue_cache(key):
    return {"identifier" : {"id" : key}, "queued": True}

def mock_success_cache(key):
    return {"identifier" : {"id" : key}, "bibjson": {"title" : "cached"}}

def mock_is_stale_false(*args, **kwargs): return False

def mock_null_cache(key): return None

@classmethod
def mock_check_archive(cls, key):
    if key == "doi:10.none": return None
    if key == "doi:10.bibjson": return {"title" : "whatever"}
    if key == "doi:10.archived": return {"title" : "archived"}

def mock_null_archive(key): return None

class mock_detect_provider(plugin.Plugin):
    def detect_provider(self, record):
        record['provider'] = {"url" : ["http://provider"]}

class mock_no_provider(plugin.Plugin):
    def detect_provider(self, record): 
        pass

class mock_other_detect(plugin.Plugin):
    def detect_provider(self, record):
        record['provider'] = {"url" : ["http://other"]}

class mock_licence_plugin(plugin.Plugin):
    sup = True
    def supports(self, provider):
        return self.sup
    def license_detect(self, record):
        record['bibjson'] = {}
        record['bibjson']['license'] = [{}]
        record['bibjson']['title'] = "mytitle"

class mock_unknown_licence_plugin(plugin.Plugin):
    __version__ = "1.0"
    _short_name = "test_workflow"
    sup = True
    def supports(self, provider):
        return self.sup
    def license_detect(self, record):
        record['bibjson'] = {}

def mock_back_end(record): pass

def mock_is_stale(bibjson):
    return bibjson["title"] == "stale"
    
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
        config.module_search_list.append("isitopenaccess.tests")
        config.module_search_list.append("tests.test_workflow")
        config.module_search_list.append("isitopenaccess.tests.test_workflow")
        current_support_request = 0
        
    def tearDown(self):
        for i in range(len(config.module_search_list)):
            if config.module_search_list[i] == "tests.test_workflow":
                del config.module_search_list[i]
                break
        for i in range(len(config.module_search_list)):
            if config.module_search_list[i] == "isitopenaccess.tests.test_workflow":
                del config.module_search_list[i]
                break
        current_support_request = 0
        
    def test_01_detect_verify_type(self):
        config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        
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
        config.canonicalisers = {"doi" : "mock_doi_canon", "pmid" : "mock_pmid_canon"}
        
        # check that we can canonicalise a doi
        record = {"identifier" : {"id" : "10.123456789", "type" : "doi"}}
        workflow._canonicalise_identifier(record)
        assert record['identifier']['canonical'] == "doi:10.123456789"
        
        # check that we can canonicalise a pmid
        record = {"identifier" : {"id" : "12345678", "type" : "pmid"}}
        workflow._canonicalise_identifier(record)
        assert record['identifier']['canonical'] == "pmid:12345678", record['identifier']['canonical']
        
    def test_03_check_cache(self):
        cache.check_cache = mock_check_cache
        cache.is_stale = mock_is_stale
        cache.invalidate = mock_invalidate
        
        record = {"identifier" : {"id" : "10.none", "type" : "doi", "canonical" : "doi:10.none"}}
        cache_copy = workflow._check_cache(record)
        assert cache_copy is None
        
        record = {"identifier" : {"id" : "10.queued", "type" : "doi", "canonical" : "doi:10.queued"}}
        cache_copy = workflow._check_cache(record)
        assert cache_copy['queued']
        
        record = {"identifier" : {"id" : "10.bibjson", "type" : "doi", "canonical" : "doi:10.bibjson"}}
        cache_copy = workflow._check_cache(record)
        assert cache_copy.has_key("bibjson")
        assert cache_copy["bibjson"]["title"] == "fresh"
        
        record = {"identifier" : {"id" : "10.stale", "type" : "doi", "canonical" : "doi:10.stale"}}
        cache_copy = workflow._check_cache(record)
        assert cache_copy is None
        
    def test_04_check_archive(self):
        models.Record.check_archive = mock_check_archive
        
        record = {"identifier" : {"id" : "10.none", "type" : "doi", "canonical" : "doi:10.none"}}
        archive_copy = workflow._check_archive(record)
        assert archive_copy is None
        
        old_is_stale = workflow._is_stale
        workflow._is_stale = mock_is_stale_false
        
        record = {"identifier" : {"id" : "10.bibjson", "type" : "doi", "canonical" : "doi:10.bibjson"}}
        archive_copy = workflow._check_archive(record)
        workflow._is_stale = old_is_stale
        
        assert archive_copy.has_key("title")
    
    def test_05_cache_success(self):
        ids = [{"id" : "10.cached"}]
        
        # set up the mocks for the first test
        config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        config.canonicalisers = {"doi" : "mock_doi_canon", "pmid" : "mock_pmid_canon"}
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
    
    def test_06_archive_success(self):
        ids = [{"id" : "10.archived"}]
        
        # set up the mocks for the first test
        config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        config.canonicalisers = {"doi" : "mock_doi_canon", "pmid" : "mock_pmid_canon"}
        cache.check_cache = mock_null_cache
        archive.check_archive = mock_check_archive
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
        
    def test_07_lookup_error(self):
        ids = [{"id" : "12345", "type" : "doi"}]
        config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        
        rs = workflow.lookup(ids)
        assert len(rs.errors) == 1
        result = rs.errors[0]
        assert result['identifier']['id'] == "12345"
        assert result['identifier']['type'] == "doi"
        assert result.has_key("error")
    
    def test_08_detect_provider(self):
        record = {"identifier" : {"id" : "12345"}}
        workflow.detect_provider(record)
        
        # the record should not have changed
        assert not record.has_key('provider')
        
        record['identifier']['type'] = "unknown"
        workflow.detect_provider(record)
        
        # the record should not have changed
        assert not "provider" in record
        
        # check that a plugin is applied
        config.provider_detection = {"doi" : ["mock_detect_provider"]}
        record['identifier']['type'] = "doi"
        workflow.detect_provider(record)
        assert "provider" in record, record
        assert "url" in record['provider']
        assert record["provider"]["url"][0] == "http://provider"
        
        # now check that the chain continues all the way to the end
        config.provider_detection = {"doi" : ["mock_no_provider", "mock_other_detect", "mock_detect_provider"]}
        del record['provider']
        workflow.detect_provider(record)
        assert "provider" in record
        assert "url" in record['provider']
        assert record["provider"]["url"][0] == "http://provider"
    
    """
    NOTE: this test superseded by test_plugin.py
    def test_09_load_provider_plugin(self):
        # FIXME: this test just about works, but is a total mess.  It relies heavily on
        # some tricky monkey patching, which is working, and the code in workflow.py
        # that it's testing is quite small, so it's probably ok.
        global who_to_support
        global current_support_request
        # first try the simple case of a dictionary of plugins
        # FIXME: note that we can't just use the function name in licence_detection, due to limitations
        # of the plugloader, so we need to give it also the name of this module
        config.licence_detection = ["test_workflow.one", "test_workflow.two"]
        who_to_support = 0
        one, nameone, versionone = workflow._get_provider_plugin({"url" : ["http://one"]})
        who_to_support = 1
        two, nametwo, versiontwo = workflow._get_provider_plugin({"url" : ["https://two"]})
        assert one() == "one"
        assert nameone == "test_workflow", nameone
        assert versionone == "1.0"
        assert two() == "two"
        
        # now try a couple of granular ones
        current_support_request = 0
        config.licence_detection = ["test_workflow.one", "test_workflow.one_two", "test_workflow.two"]
        who_to_support = 0
        one, nameone, nametwo = workflow._get_provider_plugin({"url" : ["one"]})
        who_to_support = 1
        onetwo, nameonetwo, versiononetwo = workflow._get_provider_plugin({"url" : ["one/two"]})
        current_support_request = 0
        who_to_support = 0
        otherone, nameotherone, versionotherone = workflow._get_provider_plugin({"url" : ["one/three"]})
        who_to_support = 1
        onetwothree, nameonetwothree, versiononetwothree = workflow._get_provider_plugin({"url" : ["one/two/three"]})
        assert one() == "one"
        assert onetwo() == "one_two"
        assert otherone() == "one"
        assert onetwothree() == "one_two"
    """
    
    def test_10_provider_licence(self):
        config.license_detection = ["mock_licence_plugin"]
        
        # first check that no provider results in no change
        record = {}
        workflow.provider_licence(record)
        assert not record.has_key("bibjson")
        
        # now check there's no change if there's no plugin
        mock_licence_plugin.sup = False
        record['provider'] = {"url" : ["provider"]}
        workflow.provider_licence(record)
        assert not record.has_key("bibjson")
        
        # check that it works when it's right
        mock_licence_plugin.sup = True
        record['provider'] = {"url" : ["testprovider"]}
        workflow.provider_licence(record)
        
        assert record.has_key("bibjson")
        assert record['bibjson'].has_key("license") # american spelling
        assert len(record['bibjson']['license']) == 1
        
    def test_11_provider_unknown_licence(self):
        config.license_detection = ["mock_unknown_licence_plugin"]
        
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
    
    def test_12_check_cache_update_on_queued(self):
        global CACHE
        ids = [{"id" : "10.queued"}]
        
        # set up the configuration so that the type and canonical form are created
        # but no copy of the id is found in the cache or archive
        config.type_detection = ["mock_doi_type", "mock_pmid_type"]
        config.canonicalisers = {"doi" : "mock_doi_canon", "pmid" : "mock_pmid_canon"}
        cache.check_cache = mock_null_cache
        archive.check_archive = mock_null_archive
        
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
        assert CACHE["doi:10.queued"]['queued']
        
        
        # reset the test cache and reinstate the old back-end
        del CACHE["doi:10.queued"]
        workflow._start_back_end = old_back_end
    
    def test_13_store(self):
        global CACHE
        global ARCHIVE
        
        cache.cache = mock_cache
        models.Record.store = mock_store
        
        # first check that we get the right behaviour if no licence is provided
        record = {'identifier' : {"id" : "10.1", "type" : "doi", "canonical" : "doi:10.1"}, "queued" : True}
        workflow.store_results(record)
        assert CACHE.has_key("doi:10.1")
        assert len(ARCHIVE) == 1
        assert "queued" not in record
        assert "bibjson" in record
        assert "license" in record['bibjson']
        assert record['bibjson']['license'][0]['type'] == "failed-to-obtain-license"
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
        assert "queued" not in CACHE["doi:10.1"]
        assert len(ARCHIVE) == 1
        assert ARCHIVE[0]["title"] == "mytitle"
        assert "queued" not in record
        assert "identifier" in record['bibjson']
        
        del CACHE['doi:10.1']
        del ARCHIVE[0]
    
    def test_14_chain(self):
        global CACHE
        global ARCHIVE
        
        record = {'identifier' : {"id" : "10.1", "type" : "doi", "canonical" : "doi:10.1"}, "queued" : True}
        
        config.provider_detection = {"doi" : ["mock_detect_provider"]}
        config.license_detection = ["mock_licence_plugin"]
        
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
        assert not CACHE["doi:10.1"].has_key("queued")
        assert len(ARCHIVE) == 1
        assert ARCHIVE[0]["title"] == "mytitle"
        
        del CACHE['doi:10.1']
        del ARCHIVE[0]
        
        
        
        
        
        
        
        
        
        
        
        
        
