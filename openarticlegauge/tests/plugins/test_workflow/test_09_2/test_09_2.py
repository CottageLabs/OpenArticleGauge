from openarticlegauge import plugin

class mock_detect_provider(plugin.Plugin):
    _short_name="mock_dp"
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : ["doi"],
            "license_detect" : False
        }
    def detect_provider(self, record):
        record.add_provider_url("http://provider")

class mock_no_provider(plugin.Plugin):
    _short_name="mock_np"
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : ["doi"],
            "license_detect" : False
        }
    def detect_provider(self, record): 
        pass

class mock_other_detect(plugin.Plugin):
    _short_name="mock_od"
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : ["doi"],
            "license_detect" : False
        }
    def detect_provider(self, record):
        record.add_provider_url("http://other")
