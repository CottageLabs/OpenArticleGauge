from openarticlegauge import plugin

class mock_detect_provider_error(plugin.Plugin):
    _short_name="mock"
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : ["doi"],
            "license_detect" : False
        }
        
    def detect_provider(self, record):
        raise Exception("oh dear!")
