from unittest import TestCase

import redis, json, datetime
from openarticlegauge import config, cache, models

test_host = "localhost"
test_port = 6379
test_db = 3 # we are using 1 and 2 for the celery queue and the actual cache respectively

class TestWorkflow(TestCase):

    def setUp(self):
        config.REDIS_CACHE_HOST = test_host
        config.REDIS_CACHE_PORT = test_port
        config.REDIS_CACHE_DB = test_db
        
    def tearDown(self):
        # FIXME: should probably set the config values back
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        client.delete("exists")
        client.delete("corrupt")
        
    def test_01_check_redis_up(self):
        # not really a test, but we can't carry on if redis isn't responding
        try:
            client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
            client.get("whatever")
        except:
            assert False, "redis is not responding, can't carry out test suite"
    
    def test_02_check_cache_not_exists(self):
        # check the cache for a value which doesn't exist
        result = cache.check_cache("not_exists")
        assert result is None
        
    def test_03_check_cache_exists(self):
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        obj = {"key" : "value"}
        client.set("exists", json.dumps(obj))
        
        result = cache.check_cache("exists")
        result = result.record # unpack message object
        assert result.has_key("key")
        assert result["key"] == "value"
        
        client.delete("exists")
    
    def test_04_check_cache_corrupt(self):
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        client.setex("corrupt", 2, "{askjdfafds}")
        
        result = cache.check_cache("corrupt")
        assert result is None
        
        corrupt = client.get("corrupt")
        assert corrupt is None
        
    def test_05_is_stale_unlicenced(self):
        # bibjson = {}
        record = models.MessageObject(record={"bibjson" : {}})
        assert cache.is_stale(record)
        
    def test_06_is_stale_no_dates(self):
        bibjson = {'license' : []}
        record = models.MessageObject(record={"bibjson" : bibjson})
        assert cache.is_stale(record)
        
        bibjson['license'].append({})
        bibjson['license'][0]['provenance'] = {}
        record = models.MessageObject(record={"bibjson" : bibjson})
        assert cache.is_stale(record)
        
        bibjson['license'][0]['provenance']['date'] = None
        record = models.MessageObject(record={"bibjson" : bibjson})
        assert cache.is_stale(record)
        
    def test_07_is_stale_invalid_dates(self):
        bibjson = {'license' : [{ 'provenance' : {'date' : "wibble"} }, {'provenance' : {'date' : "whatever"}}]}
        record = models.MessageObject(record={"bibjson" : bibjson})
        assert cache.is_stale(record)
    
    def test_08_is_stale_not_stale(self):
        config.licence_stale_time = 15552000 # 6 months
        
        # a record with a single date, which is not stale
        n = datetime.datetime.now() # now
        threemonths = datetime.timedelta(days=90) # 3 months
        bibjson = {'license' : [{ 'provenance' : {'date' : datetime.datetime.strftime(n - threemonths, "%Y-%m-%dT%H:%M:%SZ")}}]}
        record = models.MessageObject(record={"bibjson" : bibjson})
        assert not cache.is_stale(record), bibjson
        
        # a record with multiple dates, neither of which is stale
        fourmonths = datetime.timedelta(days=120)
        bibjson = {'license' : [
                        {'provenance' : {'date' : datetime.datetime.strftime(n - threemonths, "%Y-%m-%dT%H:%M:%SZ")}},
                        {'provenance' : {'date' : datetime.datetime.strftime(n - fourmonths, "%Y-%m-%dT%H:%M:%SZ")}}
                  ]}
        record = models.MessageObject(record={"bibjson" : bibjson})
        assert not cache.is_stale(record)
        
        # a record with multiple dates, only one of which is not stale
        oneyear = datetime.timedelta(days=365)
        bibjson = {'license' : [
                        {'provenance' : {'date' : datetime.datetime.strftime(n - threemonths, "%Y-%m-%dT%H:%M:%SZ")}},
                        {'provenance' : {'date' : datetime.datetime.strftime(n - oneyear, "%Y-%m-%dT%H:%M:%SZ")}}
                  ]}
        record = models.MessageObject(record={"bibjson" : bibjson})
        assert not cache.is_stale(record)
        
    def test_09_is_stale_stale(self):
        config.licence_stale_time = 15552000 # 6 months
        
        # a record with multiple dates, all of which are stale
        n = datetime.datetime.now() # now
        sevenmonths = datetime.timedelta(days=210) # 3 months
        oneyear = datetime.timedelta(days=365)
        bibjson = {'license' : [
                        {'provenance' : {'date' : datetime.datetime.strftime(n - sevenmonths, "%Y-%m-%dT%H:%M:%SZ")}},
                        {'provenance' : {'date' : datetime.datetime.strftime(n - oneyear, "%Y-%m-%dT%H:%M:%SZ")}}
                  ]}
        record = models.MessageObject(record={"bibjson" : bibjson})
        assert cache.is_stale(record)
        
    def test_10_cache_not_json(self):
        with self.assertRaises(cache.CacheException):
            cache.cache("exists", self) # pass in something that won't json serialise
    
    def test_11_cache(self):
        mo = models.MessageObject(record={"key" : "value"})
        cache.cache("exists", mo)
        
        client = redis.StrictRedis(host=test_host, port=test_port, db=test_db)
        s = client.get("exists")
        obj = json.loads(s)
        assert obj.has_key("key")
        assert obj["key"] == "value"
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
