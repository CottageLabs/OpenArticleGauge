from openarticlegauge import plugin
from openarticlegauge.plugins.resources.bmc_base_urls import BASE_URLS

class BMCPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin
    __desc__ = "Detects licences in the BioMed Central journals"
    
    _base_urls = BASE_URLS
    _license_mappings = [
            {
                "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited." : 
                {
                    'type': 'cc-by', 
                    'version':'2.0', 
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by/2.0'
                }
            },
            { # Same as above but has a space in the license link text
                "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'> http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited." : 
                {
                    'type': 'cc-by', 
                    'version':'2.0', 
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by/2.0'
                }
            },
            { # Same as top but 'credited' rather than cited
                "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly credited." : 
                {
                    'type': 'cc-by', 
                    'version':'2.0', 
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by/2.0'
                }
            }
        ]
    
    ## Plugin parent class overrides ##
    
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : True
        }
    
    def supports(self, provider):
        """
        Does the page_license plugin support this provider
        """    
        return self.supports_by_base_url(provider)
    
    def license_detect(self, record):
        """
        To respond to the provider identifier: http://www.biomedcentral.com
        
        This should determine the licence conditions of the BMC article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """

        # licensing statements to look for on this publisher's pages
        # take the form of {statement: meaning}
        # where meaning['type'] identifies the license (see licenses.py)
        # and meaning['version'] identifies the license version (if available)
        lic_statements = self._license_mappings
        
        # for url in record['provider']['url']:
        for url in record.provider_urls:
            if self.supports_base_url(url):
                self.simple_extract(lic_statements, record, url)

        return (self._short_name, self.__version__)
