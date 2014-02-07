from unittest import TestCase
from openarticlegauge import plugin, config, models

class DetectPlugin(plugin.Plugin):
    def type_detect_verify(self, record):
        # bibjson_identifier['type'] = "mine"
        record.identifier_type = "mine"

class CanonPlugin(plugin.Plugin):
    def canonicalise(self, record):
        # bibjson_identifier["canonical"] = bibjson_identifier["type"] + ":" + bibjson_identifier["id"]
        record.canonical = record.identifier_type + ":" + record.id

class ProviderPlugin(plugin.Plugin):
    def detect_provider(self, record):
        """
        if record["identifier"]["canonical"] == "mine:123":
            record['provider'] = {"url" : ["http://mine"]}
        """
        if record.canonical == "mine:123":
            record.add_provider_url("http://mine")
        
    def supports(self, provider):
        if "http://mine" in provider['url']:
            return True
        return False
    
    def license_detect(self, record):
        # record['bibjson'] = {"license" : {"url" : "http://license"}}
        record.add_license_object({"url" : "http://license"})

class TestPlugin(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_01_not_implemented(self):
        p = plugin.Plugin()
        
        with self.assertRaises(NotImplementedError):
            p.type_detect_verify({})
        
        with self.assertRaises(NotImplementedError):
            p.canonicalise({})
        
        with self.assertRaises(NotImplementedError):
            p.detect_provider({})
        
        with self.assertRaises(NotImplementedError):
            p.supports({})
        
        with self.assertRaises(NotImplementedError):
            p.license_detect({})
    
    def test_02_standard_properties(self):
        p = plugin.Plugin()
        
        assert p.__version__ == "0.0"
        assert p._short_name == "vanilla_plugin"
        assert p.capabilities() == {}
    
    def test_03_load_type_detect_verify(self):
        config.type_detection = [
            "openarticlegauge.tests.test_plugin.DetectPlugin"
        ]
        bjid = {}
        record = models.MessageObject(record={"identifier":  bjid})
        ps = plugin.PluginFactory.type_detect_verify()
        assert len(ps) == 1
        ps[0].type_detect_verify(record)
        assert bjid['type'] == 'mine'
    
        with self.assertRaises(NotImplementedError):
            ps[0].canonicalise({})
    
    def test_04_load_canonicalise(self):
        config.canonicalisers = {
            "mine" : "openarticlegauge.tests.test_plugin.CanonPlugin"
        }
        bjid = {"id" : "123", "type" : "mine"}
        record = models.MessageObject(record={"identifier":  bjid})
        p = plugin.PluginFactory.canonicalise("mine")
        assert p is not None
        p.canonicalise(record)
        assert bjid['canonical'] == 'mine:123'
            
    def test_05_load_detect_provider(self):
        config.provider_detection = {
            "mine" : ["openarticlegauge.tests.test_plugin.ProviderPlugin"]
        }
        record = {"identifier": {"id" : "123", "type" : "mine", "canonical" : "mine:123"}}
        record = models.MessageObject(record=record)
        ps = plugin.PluginFactory.detect_provider("mine")
        assert len(ps) == 1
        ps[0].detect_provider(record)
        record = record.record
        assert record['provider']['url'][0] == 'http://mine'
        
    def test_06_load_license_detect(self):
        config.license_detection = [
            "openarticlegauge.tests.test_plugin.ProviderPlugin"
        ]
        record = { "provider" : {"url" : ["http://mine"]}}
        record = models.MessageObject(record=record)
        p = plugin.PluginFactory.license_detect(record.provider)
        assert p is not None
        p.license_detect(record)
        record = record.record
        assert record['bibjson']['license'][0]['url'] == "http://license", record
        
    def test_06_load_no_license_detect(self):
        config.license_detection = [
            "openarticlegauge.tests.test_plugin.ProviderPlugin"
        ]
        record = { "provider" : {"url" : ["http://another"]}}
        record = models.MessageObject(record=record)
        p = plugin.PluginFactory.license_detect(record.provider)
        assert p is None
        
        
