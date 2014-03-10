import os
from unittest import TestCase
from openarticlegauge import plugin, config, models

class TestPlugin(TestCase):

    def setUp(self):
        self.old_plugin_dir = config.PLUGIN_DIR
        
    def tearDown(self):
        config.PLUGIN_DIR = self.old_plugin_dir
        plugin.PluginFactory.PLUGIN_CONFIG = None
    
    # Tests on the base plugin object
    
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
            
        caps = p.capabilities()
        assert len(caps.keys()) == 0
    
    def test_02_standard_properties(self):
        p = plugin.Plugin()
        
        assert p.__version__ == "0.0"
        assert p._short_name == "vanilla_plugin"
        assert p.capabilities() == {}
        assert p.__priority__ == 0
    
    # Tests on the PluginFactory
    
    def test_03_load_from_dir(self):
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_plugin")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        cfg = plugin.PluginFactory.PLUGIN_CONFIG
        
        # just check that the structure of the cfg is as we expect it to be
        tdv = cfg.get("type_detect_verify", [])
        assert len(tdv) == 1
        assert tdv[0]._short_name == "detect_plugin"
        
        canon = cfg.get("canonicalise", {})
        assert len(canon.keys()) == 3
        assert "doi" in canon
        assert "mine" in canon
        assert "pmid" in canon
        assert canon["doi"]._short_name == "canon_plugin"
        assert canon["mine"]._short_name == "canon_plugin"
        assert canon["pmid"]._short_name == "canon_plugin"
        
        dp = cfg.get("detect_provider", {})
        assert len(dp.keys()) == 1
        assert "mine" in dp
        assert len(dp["mine"]) == 1
        assert dp["mine"][0]._short_name == "provider_plugin"
        
        ld = cfg.get("license_detect", [])
        assert len(ld) == 1
        assert ld[0]._short_name == "provider_plugin"
        
    def test_04_load_type_detect_verify(self):
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_plugin")
        config.PLUGIN_DIR = pdir
        
        bjid = {}
        record = models.MessageObject(record={"identifier":  bjid})
        ps = plugin.PluginFactory.type_detect_verify()
        assert len(ps) == 1, ps
        ps[0].type_detect_verify(record)
        assert bjid['type'] == 'mine'
    
        with self.assertRaises(NotImplementedError):
            ps[0].canonicalise({})
    
    def test_05_load_canonicalise(self):
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_plugin")
        config.PLUGIN_DIR = pdir
        
        bjid = {"id" : "123", "type" : "mine"}
        record = models.MessageObject(record={"identifier":  bjid})
        p = plugin.PluginFactory.canonicalise("mine")
        assert p is not None
        p.canonicalise(record)
        assert bjid['canonical'] == 'mine:123'
            
    def test_06_load_detect_provider(self):
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_plugin")
        config.PLUGIN_DIR = pdir
        
        record = {"identifier": {"id" : "123", "type" : "mine", "canonical" : "mine:123"}}
        record = models.MessageObject(record=record)
        ps = plugin.PluginFactory.detect_provider("mine")
        assert len(ps) == 1
        ps[0].detect_provider(record)
        record = record.record
        assert record['provider']['url'][0] == 'http://mine'
        
    def test_07_load_license_detect(self):
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_plugin")
        config.PLUGIN_DIR = pdir
        
        record = { "provider" : {"url" : ["http://mine"]}}
        record = models.MessageObject(record=record)
        p = plugin.PluginFactory.license_detect(record.provider)
        assert p is not None
        p.license_detect(record)
        record = record.record
        assert record['bibjson']['license'][0]['url'] == "http://license", record
        
    def test_08_load_no_license_detect(self):
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_plugin")
        config.PLUGIN_DIR = pdir
        
        record = { "provider" : {"url" : ["http://another"]}}
        record = models.MessageObject(record=record)
        p = plugin.PluginFactory.license_detect(record.provider)
        assert p is None
    
    def test_09_priority(self):
        pdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins", "test_plugin")
        plugin.PluginFactory.load_from_directory(plugin_dir=pdir)
        cfg = plugin.PluginFactory.PLUGIN_CONFIG
        
        assert cfg["all"][2]._short_name == "detect_plugin", cfg["all"]
        assert cfg["all"][2].__priority__ == -100
        
        assert cfg["all"][1]._short_name == "canon_plugin"
        assert cfg["all"][1].__priority__ == 0
        
        assert cfg["all"][0]._short_name == "provider_plugin"
        assert cfg["all"][0].__priority__ == 1000
        
        
