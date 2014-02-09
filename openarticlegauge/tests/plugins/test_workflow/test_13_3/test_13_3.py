from openarticlegauge import plugin

class mock_licence_plugin_error(plugin.Plugin):
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : True
        }
    def supports(self, provider):
        return True
    def license_detect(self, record):
        raise Exception("oh dear!")
