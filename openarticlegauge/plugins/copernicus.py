"""
This plugin handles Copernicus Publications articles.
"""

from openarticlegauge import plugin

class COPERNICUSPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' 
    __desc__ = "Handles Copernicus Publications articles"
        
    _base_urls = ["www.atmos-chem-phys.net"]
    _license_mappings = [
            {"under the Creative Commons Attribution 3.0 License":
                {'type': 'cc-by', 
                 'version':'3.0', 
                'url': 'http://creativecommons.org/licenses/by/3.0'}
            }
        ]
    
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : True
        }

    def supports(self, provider):
        """
        Does this plugin support this provider
        """
        return self.supports_by_base_url(provider)

    def license_detect(self, record):
        """
        To respond to the provider identifier: http://atmos-chem-phys.net
        
        This should determine the licence conditions of the ACP article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """
 
        lic_statements = self._license_mappings
       
        for url in record.provider_urls:
            if self.supports_base_url(url):
                self.simple_extract(lic_statements, record, url)

        return (self._short_name, self.__version__)