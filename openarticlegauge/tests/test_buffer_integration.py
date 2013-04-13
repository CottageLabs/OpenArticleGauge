########################################################################################
# Before running these tests, you must start all of the infrastructure with the
# storage buffering turned ON
#
# BUFFERING = True
# BUFFER_FLUSH_PERIOD=6
# BUFFER_GRACE_PERIOD=5
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

    def setUp(self):
        self.buffer = config.BUFFERING
        self.flush = config.BUFFER_FLUSH_PERIOD
        self.grace = config.BUFFER_GRACE_PERIOD

        config.BUFFERING = True
        config.BUFFER_FLUSH_PERIOD = 6
        config.BUFFER_GRACE_PERIOD = 5
        
        config.redis_cache_host = test_host
        config.redis_cache_port = test_port
        config.redis_cache_db = test_db
        
    def tearDown(self):
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        client.delete("doi:10.success/1")
        client.delete("doi:10.queued/1")
        client.delete("doi:10.cached/1")
        client.delete("doi:10.stale/1")
        client.delete("doi:10.archived/1")
        client.delete("doi:10.1371/journal.pone.0035089")
        
        models.Record(id="doi:10.stale_1").delete()
        models.Record(id="doi:10.archived_1").delete()
        models.Record(id="doi:10.1371_journal.pone.0035089").delete()
        
        config.BUFFERING = self.buffer
        config.BUFFER_FLUSH_PERIOD = self.flush
        config.BUFFER_GRACE_PERIOD = self.grace
    
    def test_01_lookup_cache_buffered_archive(self):
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
        
        # set up the test archive (which will put these things into the buffer)
        models.Record.store(updated_stale)
        models.Record.store(archived)
        
        resp = requests.post(lookup_url + "10.cached/1,10.queued/1,10.stale/1,10.archived/1")
        obj = json.loads(resp.text)
        
        # even though the buffer has not yet been written to the archive, the buffer itself
        # should behave as though it is the archive, from the point of view of the rest of
        # the app, so we expect the same results as the unbuffered version
        assert obj["requested"] == 4, json.dumps(obj, indent=2)
        assert len(obj["results"]) == 3, json.dumps(obj, indent=2) # expect: cached, stale (updated version), archived
        assert len(obj["processing"]) == 1, json.dumps(obj, indent=2) # expect: queued
    
    def test_02_lookup_cache_actual_archive(self):
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
        
        # set up the test archive (which will put these things into the buffer)
        models.Record.store(updated_stale)
        models.Record.store(archived)
        
        resp = requests.post(lookup_url + "10.cached/1,10.queued/1,10.stale/1,10.archived/1")
        obj = json.loads(resp.text)
        
        # even though the buffer has not yet been written to the archive, the buffer itself
        # should behave as though it is the archive, from the point of view of the rest of
        # the app, so we expect the same results as the unbuffered version
        assert obj["requested"] == 4, json.dumps(obj, indent=2)
        assert len(obj["results"]) == 3, json.dumps(obj, indent=2) # expect: cached, stale (updated version), archived
        assert len(obj["processing"]) == 1, json.dumps(obj, indent=2) # expect: queued
        
        # now we need to wait for the buffer to flush before making our next corroborating request
        time.sleep(31)
        
        # now do the same request again, and expect the same results
        resp = requests.post(lookup_url + "10.cached/1,10.queued/1,10.stale/1,10.archived/1")
        obj = json.loads(resp.text)
        
        # even though the buffer has not yet been written to the archive, the buffer itself
        # should behave as though it is the archive, from the point of view of the rest of
        # the app, so we expect the same results as the unbuffered version
        assert obj["requested"] == 4, json.dumps(obj, indent=2)
        assert len(obj["results"]) == 3, json.dumps(obj, indent=2) # expect: cached, stale (updated version), archived
        assert len(obj["processing"]) == 1, json.dumps(obj, indent=2) # expect: queued
