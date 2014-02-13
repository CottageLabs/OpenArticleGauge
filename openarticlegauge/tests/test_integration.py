########################################################################################
# Before running these tests, you must start all of the infrastructure with the
# storage buffering turned OFF
#
# FIXME: we need a better way of starting and re-configuring the running application
# within Celery, but that is less important than getting the app actually working, so
# this clunky integration test will have to suffice for the moment
########################################################################################

from unittest import TestCase

from openarticlegauge import workflow, config, models, cache
import redis, json, datetime, requests, uuid, time

test_host = "localhost"
test_port = 6379
test_db = 2 # use the real cache database, since this is an integration tests

lookup_url = "http://localhost:5000/lookup/"

class TestIntegration(TestCase):

    # should add a test to include buffering ...

    def setUp(self):
        self.buffer = config.BUFFERING
        config.BUFFERING = False
        config.redis_cache_host = test_host
        config.redis_cache_port = test_port
        config.redis_cache_db = test_db
        models.Record.refresh()
        
    def tearDown(self):
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        client.delete("doi:10.success/1")
        client.delete("doi:10.queued/1")
        client.delete("doi:10.cached/1")
        client.delete("doi:10.stale/1")
        client.delete("doi:10.archived/1")
        client.delete("doi:10.1371/journal.pone.0035089")
        models.Record.refresh()
        models.Record(id="doi:10.stale_1").delete()
        models.Record(id="doi:10.archived_1").delete()
        models.Record(id="doi:10.1371_journal.pone.0035089").delete()
        models.Record.refresh()
        config.BUFFERING = self.buffer
        
    def test_01_http_lookup_cache_only(self):
        # The various vectors we want to test
        # - a successful cached and in-date record
        # - a cached record wihch is queued
        now = datetime.datetime.now()
        success = {
            "identifier" : {"id" : "10.success/1", "type" : "doi", "canonical" : "doi:10.success/1"}, 
            "bibjson" : {"title" : "mytitle", 
                "license" : [{
                    "provenance" : {
                        "date" : datetime.datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
                    }
                }]
            }
        }
        queued = {
            "identifier" : {"id" : "10.queued/1", "type" : "doi", "canonical" : "doi:10.queued/1"}, 
            "queued" : True
        }
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        client.set("doi:10.success/1", json.dumps(success))
        client.set("doi:10.queued/1", json.dumps(queued))
        
        resp = requests.post(lookup_url + "10.success/1,10.queued/1")
        obj = json.loads(resp.text)
        
        assert obj["requested"] == 2
        assert len(obj["results"]) == 1
        assert len(obj["processing"]) == 1
    
    def test_02_http_lookup_cache_archive(self):
        # The various vectors we want to test
        # - a successful cached and in-date record
        # - a cached record which is queued
        # - a cached record which is stale, but which has an updated version in the archive
        # - a record which is in the archive but not the cache, and which is in-date
        now = datetime.datetime.now()
        year = datetime.timedelta(days=365)
        cached = {
            "identifier" : {"id" : "10.cached/1", "type" : "doi", "canonical" : "doi:10.cached/1"}, 
            "bibjson" : {"title" : "mytitle", 
                "license" : [{
                    "provenance" : {
                        "date" : datetime.datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
                    }
                }]
            }
        }
        queued = {
            "identifier" : {"id" : "10.queued/1", "type" : "doi", "canonical" : "doi:10.queued/1"}, 
            "queued" : True
        }
        stale = {
            "identifier" : {"id" : "10.stale/1", "type" : "doi", "canonical" : "doi:10.stale/1"}, 
            "bibjson" : {"title" : "another title", 
                "license" : [{
                    "provenance" : {
                        "date" : datetime.datetime.strftime(now - year, "%Y-%m-%dT%H:%M:%SZ")
                    }
                }]
            }
        }
        updated_stale = {
            "identifier" : [{"id" : "10.stale/1", "type" : "doi", "canonical" : "doi:10.stale/1"}],
            "title" : "updated",
            "license" : [{
                "provenance" : {
                    "date" : datetime.datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
                }
            }]
        }
        archived = {
            "identifier" : [{"id" : "10.archived/1", "type" : "doi", "canonical" : "doi:10.archived/1"}],
            "title" : "archived",
            "license" : [{
                "provenance" : {
                    "date" : datetime.datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
                }
            }]
        }
        
        # set up the test cache
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        client.set("doi:10.cached/1", json.dumps(cached))
        client.set("doi:10.queued/1", json.dumps(queued))
        client.set("doi:10.stale/1", json.dumps(stale))
        
        # set up the test archive
        models.Record.store(updated_stale)
        models.Record.store(archived)
        
        resp = requests.post(lookup_url + "10.cached/1,10.queued/1,10.stale/1,10.archived/1")
        obj = json.loads(resp.text)
        
        assert obj["requested"] == 4, json.dumps(obj, indent=2)
        assert len(obj["results"]) == 3, json.dumps(obj, indent=2) # expect: cached, stale (updated version), archived
        assert len(obj["processing"]) == 1, json.dumps(obj, indent=2) # expect: queued
        
    def test_03_back_end(self):
        # kick off a known good doi lookup
        record = {"identifier" : {"id" : "http://dx.doi.org/10.1371/journal.pone.0035089", "type" : "doi", "canonical" : "doi:10.1371/journal.pone.0035089"}, "queued" : True}
        record = models.MessageObject(record=record)
        a = workflow._start_back_end(record)
        
        # wait for the process to finish
        waited = 0
        while not a.ready():
            time.sleep(0.2)
            waited += 0.2
            assert waited < 10 # only give it 10 seconds, max, that should be easily enough
        
        # now we need to wait until the buffer itself gets flushed
        time.sleep(config.BUFFER_FLUSH_PERIOD)
        
        # we should find the record in the async result, the archive, and the cache
        async_result = a.result
        assert async_result['identifier']['canonical'] == "doi:10.1371/journal.pone.0035089"
        assert not async_result.get("queued", False)
        #assert "queued" not in async_result
        assert async_result["bibjson"]["identifier"][0]["canonical"] == "doi:10.1371/journal.pone.0035089"
        assert async_result["bibjson"]["license"][0]["title"] == "UK Open Government Licence (OGL)"
        
        archive_result = models.Record.check_archive("doi:10.1371/journal.pone.0035089")
        assert archive_result["identifier"][0]["canonical"] == "doi:10.1371/journal.pone.0035089"
        assert archive_result["license"][0]["title"] == "UK Open Government Licence (OGL)"
        
        cached_result = cache.check_cache("doi:10.1371/journal.pone.0035089")
        cached_result = cached_result.record
        assert cached_result['identifier']['canonical'] == "doi:10.1371/journal.pone.0035089"
        assert not cached_result.get("queued", False)
        #assert "queued" not in cached_result
        assert cached_result["bibjson"]["identifier"][0]["canonical"] == "doi:10.1371/journal.pone.0035089"
        assert cached_result["bibjson"]["license"][0]["title"] == "UK Open Government Licence (OGL)"
    
    def test_04_processing(self):
        # make the request, and then immediately look up the id in the cache
        resp = requests.post(lookup_url + "10.1371/journal.pone.0035089")
        cached_result = cache.check_cache("doi:10.1371/journal.pone.0035089")
        cached_result = cached_result.record
        
        # make some assertions about the response and then the cached record (that it is queued)
        
        obj = json.loads(resp.text)
        assert len(obj["processing"]) == 1, obj
        assert cached_result['identifier']['canonical'] == "doi:10.1371/journal.pone.0035089"
        assert cached_result.get("queued", False)
        #assert "queued" in cached_result
    
    def test_05_recheck(self):
        # make the request, and then immediately look up the id in the cache
        resp = requests.post(lookup_url + "10.1371/journal.pone.0035089")
        
        queued = True
        waited = 0
        while queued:
            time.sleep(0.2)
            waited += 0.2
            cached_result = cache.check_cache("doi:10.1371/journal.pone.0035089")
            cached_result = cached_result.record
            queued = cached_result.get("queued", False)
            assert waited < 10 # only give it 10 seconds, max, that should be easily enough
        
        # now we need to wait until the buffer itself gets flushed
        time.sleep(config.BUFFER_FLUSH_PERIOD)
        
        archive_result = models.Record.check_archive("doi:10.1371/journal.pone.0035089")
        assert archive_result["identifier"][0]["canonical"] == "doi:10.1371/journal.pone.0035089"
        assert archive_result["license"][0]["title"] == "UK Open Government Licence (OGL)"
        
        cached_result = cache.check_cache("doi:10.1371/journal.pone.0035089")
        cached_result = cached_result.record
        assert cached_result['identifier']['canonical'] == "doi:10.1371/journal.pone.0035089"
        assert not cached_result.get("queued", False)
        #assert "queued" not in cached_result
        assert cached_result["bibjson"]["identifier"][0]["canonical"] == "doi:10.1371/journal.pone.0035089"
        assert cached_result["bibjson"]["license"][0]["title"] == "UK Open Government Licence (OGL)"
        
        # now we know it is done, re-request the result set
        resp = requests.post(lookup_url + "10.1371/journal.pone.0035089")
        obj = json.loads(resp.text)
        
        assert len(obj["results"]) == 1
        assert len(obj["processing"]) == 0
        assert len(obj["errors"]) == 0
        assert obj["requested"] == 1
    
    ''' 
    Commented out for the time being, as there seems to be a problem with the test causing it
    to ERROR out
    def test_06_known_failures_cell_reports(self):
        """
        Make sure that the error information of plugins which always fail due
        to publishers not publishing license info (or similar) is properly
        present when such a DOI is handed to us.

        This particular test ensures that failure info from the Cell Reports
        plugin is present when a Cell Reports DOI is looked up.
        """
        from openarticlegauge.plugins.cell_reports import CellReportsPlugin
        expected_error_message = CellReportsPlugin.fail_why
        expected_suggested_solution = CellReportsPlugin.fail_suggested_solution

        resp = requests.get(lookup_url + "10.1016/j.celrep.2012.11.027" + '.json')
        time.sleep(10) # wait for the app to process the request
        resp = requests.get(lookup_url + "10.1016/j.celrep.2012.11.027" + '.json')

        result = json.loads(resp.text)
        assert 'license' in result['results'][-1]
        assert len(result['results'][-1]['license']) > 0

        assert result['results'][-1]['license'][-1]['type'] == 'failed-to-obtain-license'

        assert 'error_message' in result['results'][-1]['license'][-1]
        assert 'suggested_solution' in result['results'][-1]['license'][-1]
        assert result['results'][-1]['license'][-1]['error_message'] == expected_error_message
        assert result['results'][-1]['license'][-1]['suggested_solution'] == expected_suggested_solution
    '''
