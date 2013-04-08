from unittest import TestCase

from isitopenaccess import models
from isitopenaccess import config
import json, redis, time

ARCHIVE = []
@classmethod
def mock_bulk(cls, bibjson_list):
    global ARCHIVE
    ARCHIVE += bibjson_list

@classmethod
def mock_bulk_blocked(cls, bibjson_list):
    global ARCHIVE
    ARCHIVE.append(bibjson_list)

@classmethod
def mock_pull(cls, identifier):
    return None

class TestWorkflow(TestCase):

    def setUp(self):
        global ARCHIVE
        ARCHIVE = []
        self.buffering = config.BUFFERING
        self.bulk = models.Record.bulk
        self.pull = models.Record.pull
        
    def tearDown(self):
        global ARCHIVE
        ARCHIVE = []
        config.BUFFERING = self.buffering
        models.Record.bulk = self.bulk
        models.Record.pull = self.pull
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        client.delete("id_doi:123")
        client.delete("id_doi:456")
        client.delete("id_doi:789")
        client.delete("flush_buffer_lock")
        
    def test_01_resultset_init(self):
        rs = models.ResultSet()
        assert rs.requested == 0
        assert len(rs.results) == 0
        assert len(rs.errors) == 0
        assert len(rs.processing) == 0
        
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}]
        rs = models.ResultSet(ids)
        assert rs.requested == 3
        assert len(rs.results) == 0
        assert len(rs.errors) == 0
        assert len(rs.processing) == 0
    
    def test_02_resultset_results(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}]
        rs = models.ResultSet(ids)
        
        result = {
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : { "url" : ["http://www.hindawi.com/article"]},
                    "bibjson" : {"title" :  "my title"}
                 }
        rs.add_result_record(result)
        
        assert rs.requested == 3
        assert len(rs.results) == 1
        assert len(rs.errors) == 0
        assert len(rs.processing) == 0
        
        bibjson = rs.results[0]
        assert bibjson.has_key("title")
        assert bibjson["title"] == "my title"
        assert bibjson.has_key("identifier")
        assert len(bibjson["identifier"]) == 1
        assert bibjson["identifier"][0].has_key("id")
        assert bibjson["identifier"][0].has_key("type")
        assert bibjson["identifier"][0].has_key("canonical")
        
    def test_03_resultset_errors(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}]
        rs = models.ResultSet(ids)
        
        result = {
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : {"url" : ["http://www.hindawi.com/article"]},
                    "error" : "broken"
                 }
        rs.add_result_record(result)
        
        assert rs.requested == 3
        assert len(rs.results) == 0
        assert len(rs.errors) == 1
        assert len(rs.processing) == 0
        
        error = rs.errors[0]
        assert error.has_key("error")
        assert error["error"] == "broken"
        assert error.has_key("identifier")
        assert error["identifier"].has_key("id")
        
    def test_04_resultset_processing(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}]
        rs = models.ResultSet(ids)
        
        result = {
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : {"url" : ["http://www.hindawi.com/article"]},
                    "queued" : True
                 }
        rs.add_result_record(result)
        
        assert rs.requested == 3
        assert len(rs.results) == 0
        assert len(rs.errors) == 0
        assert len(rs.processing) == 1
        
        queued = rs.processing[0]
        assert queued.has_key("identifier")
        assert queued["identifier"].has_key("id")
    
    def test_05_resultset_mixed(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}, {"id" : "4"}]
        rs = models.ResultSet(ids)
        
        results = []
        results.append({
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : {"url" : ["http://www.hindawi.com/article"]},
                    "bibjson" : {"title" :  "my title"}
                 })
                 
        results.append({
                    "identifier" : {"id" : "2", "type" : "doi", "canonical" : "doi:2"},
                    "provider" : { "url" : ["http://www.hindawi.com/article"]},
                    "error" : "broken"
                 })
        
        results.append({
                    "identifier" : {"id" : "3", "type" : "doi", "canonical" : "doi:3"},
                    "provider" : { "url" : ["http://www.hindawi.com/article"]},
                    "queued" : True
                 })
        
        results.append({
                "identifier" : {"id" : "4", "type" : "doi", "canonical" : "doi:4"},
                "provider" : {"url" : ["http://www.hindawi.com/hello"]},
                "bibjson" : {"title" :  "another title"}
            })
            
        for result in results:
            rs.add_result_record(result)
    
        assert rs.requested == 4
        assert len(rs.results) == 2
        assert len(rs.errors) == 1
        assert len(rs.processing) == 1
        
        assert rs.results[0]['title'] in ["my title", "another title"]
        
    
    def test_06_resultset_json(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}, {"id" : "4"}]
        rs = models.ResultSet(ids)
        
        results = []
        results.append({
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : {"url" : ["http://www.hindawi.com/article"]},
                    "bibjson" : {"title" :  "my title"}
                 })
                 
        results.append({
                    "identifier" : {"id" : "2", "type" : "doi", "canonical" : "doi:2"},
                    "provider" : {"url" : ["http://www.hindawi.com/article"]},
                    "error" : "broken"
                 })
        
        results.append({
                    "identifier" : {"id" : "3", "type" : "doi", "canonical" : "doi:3"},
                    "provider" : {"url" : ["http://www.hindawi.com/article"]},
                    "queued" : True
                 })
        
        results.append({
                "identifier" : {"id" : "4", "type" : "doi", "canonical" : "doi:4"},
                "provider" : { "url" : ["http://www.hindawi.com/hello"]},
                "bibjson" : {"title" :  "another title"}
            })
            
        for result in results:
            rs.add_result_record(result)
            
        j = rs.json()
        obj = json.loads(j)
        
        assert obj['requested'] == 4
        assert len(obj['results']) == 2
        assert len(obj['errors']) == 1
        assert len(obj['processing']) == 1
    
    def test_07_store_with_buffering(self):
        config.BUFFERING = True
        
        record = {"identifier" : [{"canonical" : "doi:123"}]}
        models.Record.store(record)
        
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        s = client.get("id_doi:123")
        assert s is not None
        
        obj = json.loads(s)
        assert obj["identifier"][0]["canonical"] == "doi:123"
    
    def test_08_check_archive_with_buffering(self):
        config.BUFFERING = True
        
        record = {"identifier" : [{"canonical" : "doi:123"}]}
        models.Record.store(record)
        
        obj = models.Record.check_archive("doi:123")
        assert obj["identifier"][0]["canonical"] == "doi:123"
    
    def test_09_record_flush_buffer(self):
        config.BUFFERING = True
        models.Record.bulk = mock_bulk
        models.Record.pull = mock_pull
        global ARCHIVE
        
        # first check that it returns False if there's nothing to process
        result = models.Record.flush_buffer()
        assert not result
        
        # load some records into the buffer
        records = [
            {"identifier" : [{"canonical" : "doi:123"}]},
            {"identifier" : [{"canonical" : "doi:456"}]}
        ]
        for record in records:
            models.Record.store(record)
        
        # run the flush buffer and check that it executes successfully
        result = models.Record.flush_buffer()
        assert result
        
        # check that the 2 items in the buffer are now in the archive
        assert len(ARCHIVE) == 2, ARCHIVE
        for record in ARCHIVE:
            assert record['identifier'][0]['canonical'] in ["doi:123", "doi:456"]
        
        # check that the buffer is empty
        obj1 = models.Record.check_archive("doi:123")
        obj2 = models.Record.check_archive("doi:456")
        assert obj1 is None, obj1
        assert obj2 is None, obj2
    
    def test_10_record_flush_buffer_timeouts(self):
        config.BUFFERING = True
        models.Record.bulk = mock_bulk
        models.Record.pull = mock_pull
        global ARCHIVE
        
        # load some records into the buffer
        records = [
            {"identifier" : [{"canonical" : "doi:123"}]},
            {"identifier" : [{"canonical" : "doi:456"}]}
        ]
        for record in records:
            models.Record.store(record)
        
        # run the flush buffer and check that it executes successfully with a 30 second timeout
        result = models.Record.flush_buffer(key_timeout=30)
        assert result
        
        # check that the 2 items in the buffer are now in the archive
        assert len(ARCHIVE) == 2, ARCHIVE
        for record in ARCHIVE:
            assert record['identifier'][0]['canonical'] in ["doi:123", "doi:456"]
        
        # check that the items are also still in the buffer
        obj1 = models.Record.check_archive("doi:123")
        obj2 = models.Record.check_archive("doi:456")
        assert obj1['identifier'][0]['canonical'] in ["doi:123", "doi:456"]
        assert obj2['identifier'][0]['canonical'] in ["doi:123", "doi:456"]
    
    def test_11_record_flush_buffer_block_sizes(self):
        config.BUFFERING = True
        models.Record.bulk = mock_bulk_blocked
        models.Record.pull = mock_pull
        global ARCHIVE
        
        # load some records into the buffer
        records = [
            {"identifier" : [{"canonical" : "doi:123"}]},
            {"identifier" : [{"canonical" : "doi:456"}]},
            {"identifier" : [{"canonical" : "doi:789"}]}
        ]
        for record in records:
            models.Record.store(record)
            
        # run the flush buffer and check that it executes successfully with a block size of 2
        result = models.Record.flush_buffer(block_size=2)
        assert result
        
        assert len(ARCHIVE) == 2, ARCHIVE # the archive in this case is a list of lists, and there should be 2 lists
        assert len(ARCHIVE[0]) == 2 # the first block should have been 2 long
        assert len(ARCHIVE[1]) == 1 # the second block should have been 1 long
        
        # slightly convuluted way of checking that each identifier is in the archive exactly once
        canonicals = []
        for record in ARCHIVE[0]:
            assert record['identifier'][0]['canonical'] in ["doi:123", "doi:456", "doi:789"]
            canonicals.append(record['identifier'][0]['canonical'])
        assert ARCHIVE[1][0]['identifier'][0]['canonical'] in ["doi:123", "doi:456", "doi:789"]
        canonicals.append(ARCHIVE[1][0]['identifier'][0]['canonical'])
        
        assert "doi:123" in canonicals
        assert "doi:456" in canonicals
        assert "doi:789" in canonicals
        
    def test_12_celery_flush_buffer_no_buffering(self):
        config.BUFFERING = False
        result = models.flush_buffer()
        assert not result
    
    def test_13_celery_flush_buffer_prelocked(self):
        config.BUFFERING = True
        
        # manually set a lock on the process
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        client.set("flush_buffer_lock", "lock")
        
        result = models.flush_buffer()
        assert not result
        
    def test_14_celery_flush_buffer_success(self):
        config.BUFFERING = True
        config.BUFFER_GRACE_PERIOD = 30
        config.BUFFER_BLOCK_SIZE = 2
        models.Record.bulk = mock_bulk_blocked
        models.Record.pull = mock_pull
        global ARCHIVE
        
        # load some records into the buffer
        records = [
            {"identifier" : [{"canonical" : "doi:123"}]},
            {"identifier" : [{"canonical" : "doi:456"}]},
            {"identifier" : [{"canonical" : "doi:789"}]}
        ]
        for record in records:
            models.Record.store(record)
        
        result = models.flush_buffer()
        assert result
        
        # check that everything got archived
        assert len(ARCHIVE) == 2, ARCHIVE # the archive in this case is a list of lists, and there should be 2 lists
        assert len(ARCHIVE[0]) == 2 # the first block should have been 2 long
        assert len(ARCHIVE[1]) == 1 # the second block should have been 1 long
        
        # check that the things are still in the buffer
        obj1 = models.Record.check_archive("doi:123")
        obj2 = models.Record.check_archive("doi:456")
        obj3 = models.Record.check_archive("doi:789")
        assert obj1['identifier'][0]['canonical'] in ["doi:123", "doi:456", "doi:789"]
        assert obj2['identifier'][0]['canonical'] in ["doi:123", "doi:456", "doi:789"]
        assert obj3['identifier'][0]['canonical'] in ["doi:123", "doi:456", "doi:789"]
        
        # check that the lock is still set
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        lock = client.get("flush_buffer_lock")
        assert lock is not None
        
    def test_15_celery_flush_buffer_trip_lock(self):
        config.BUFFERING = True
        config.BUFFER_GRACE_PERIOD = 2
        config.BUFFER_BLOCK_SIZE = 2
        models.Record.bulk = mock_bulk_blocked
        models.Record.pull = mock_pull
        global ARCHIVE
        
        # load some records into the buffer
        records = [
            {"identifier" : [{"canonical" : "doi:123"}]},
            {"identifier" : [{"canonical" : "doi:456"}]},
            {"identifier" : [{"canonical" : "doi:789"}]}
        ]
        for record in records:
            models.Record.store(record)
        
        # run the thing the first time
        result = models.flush_buffer()
        assert result
        
        # now straight away run it a second time, which should trip the lock
        result2 = models.flush_buffer()
        assert not result2
        
        # now wait until the lock should be released and try again
        time.sleep(2.1)
        result3 = models.flush_buffer()
        assert result3
        
