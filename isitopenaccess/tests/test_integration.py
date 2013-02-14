from unittest import TestCase

from isitopenaccess import workflow, config
import redis, json, datetime, requests

test_host = "localhost"
test_port = 6379
test_db = 3 # we are using 1 and 2 for the celery queue and the actual cache respectively

class TestWorkflow(TestCase):

    def setUp(self):
        config.redis_cache_host = test_host
        config.redis_cache_port = test_port
        config.redis_cache_db = test_db
        
    def tearDown(self):
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        client.delete("doi:10.success/1")
        
    def test_01_lookup_cache_only(self):
        # The various vectors we want to test
        # - a successful cached and in-date record
        # - a cached record which is stale
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
        
        ids = [
            {"id" : "10.success/1"},
            {"id" : "10.queued/1"}
        ]
        rs = workflow.lookup(ids)
        
        assert len(rs.results) == 1
        assert len(rs.processing) == 1
        
