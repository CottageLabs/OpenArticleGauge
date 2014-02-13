from openarticlegauge import plugin

class DetectPlugin(plugin.Plugin):
    __version__ = "1.0"
    _short_name = "detect_plugin"
    def capabilities(self):
        return {
            "type_detect_verify" : True,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : False
        }
    
    def type_detect_verify(self, record):
        record.identifier_type = "mine"

class CanonPlugin(plugin.Plugin):
    __version__ = "1.0"
    _short_name = "canon_plugin"
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : ["doi", "pmid", "mine"],
            "detect_provider" : [],
            "license_detect" : False
        }
        
    def canonicalise(self, record):
        record.canonical = record.identifier_type + ":" + record.id

class ProviderPlugin(plugin.Plugin):
    __version__ = "1.0"
    _short_name = "provider_plugin"
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : ["mine"],
            "license_detect" : True
        }
        
    def detect_provider(self, record):
        if record.canonical == "mine:123":
            record.add_provider_url("http://mine")
        
    def supports(self, provider):
        if "http://mine" in provider['url']:
            return True
        return False
    
    def license_detect(self, record):
        record.add_license_object({"url" : "http://license"})
