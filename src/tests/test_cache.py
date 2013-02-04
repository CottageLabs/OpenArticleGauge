from unittest import TestCase

import redis, json
import config, cache

test_host = "localhost"
test_port = 6379
test_db = 3 # we are using 1 and 2 for the celery queue and the actual cache respectively

class TestWorkflow(TestCase):

    def setUp(self):
        config.redis_cache_host = test_host
        config.redis_cache_port = test_port
        config.redis_cache_db = test_db
        
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
        client.setex("exists", 2, json.dumps(obj))
        
        result = cache.check_cache("exists")
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
