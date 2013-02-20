from unittest import TestCase

from isitopenaccess import workflow, config, archive
import redis, json, datetime, requests, uuid

test_host = "localhost"
test_port = 6379
test_db = 2 # use the real cache database, since this is an integration tests

lookup_url = "http://localhost:5000/lookup/"

class TestWorkflow(TestCase):

    def setUp(self):
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
        # - a cached record wihch is queued
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
        updated = {
            "_id" : str(uuid.uuid4()),
            "identifier" : {"id" : "10.stale/1", "type" : "doi", "canonical" : "doi:10.stale/1"},
            "title" : "updated",
            "license" : [{
                "provenance" : {
                    "date" : datetime.datetime.strftime(now, "%Y-%m-%dT%H:%M:%SZ")
                }
            }]
        }
        archived = {
            "_id" : str(uuid.uuid4()),
            "identifier" : {"id" : "10.archived/1", "type" : "doi", "canonical" : "doi:10.archived/1"},
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
        archive.store(updated)
        archive.store(archived)
        
        resp = requests.post(lookup_url + "10.cached/1,10.queued/1,10.stale/1,10.archived/1")
        obj = json.loads(resp.text)
        
        assert obj["requested"] == 4
        assert len(obj["results"]) == 3, obj
        assert len(obj["processing"]) == 1
        
