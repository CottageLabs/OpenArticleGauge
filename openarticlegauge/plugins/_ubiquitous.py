"""
This plugin (tries to) handle all items which no other plugin picked
up.
"""
from openarticlegauge import plugin

import requests

class UbiquitousPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' 
    __desc__ = "Attempts to match generic licence strings to known licences"
    __priority__ = -2000
    
    _license_mappings = [
            {'licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License':
                {'type': 'cc-nc-sa',
                 'version':'3.0',
                 'url': 'http://creativecommons.org/licenses/by-nc-sa/3.0/'}
            },
            {'licensed under a Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License':
                {'type': 'cc-nc-nd',
                         'version':'3.0',
                         'url': 'http://creativecommons.org/licenses/by-nc-nd/3.0/'}
            },
            {'licensed under a Creative Commons Attribution 3.0 Unported License':
                {'type': 'cc-by',
                         'version':'3.0',
                         'url': 'http://creativecommons.org/licenses/by/3.0/'}
            },
            {"under the Creative Commons Attribution 3.0 License":
                {'type': 'cc-by', 
                 'version':'3.0', 
                 'url': 'http://creativecommons.org/licenses/by/3.0'}
            },
            {"under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>)":
                {'type': 'cc-by', 
                 'version':'2.0', 
                 'url': 'http://creativecommons.org/licenses/by/2.0'}
            },
            {"under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/)":
                {'type': 'cc-by', 
                 'version':'3.0', 
                 'url': 'http://creativecommons.org/licenses/by/3.0'}
            },
            {'under the terms of the Creative Commons Attribution License <br/>(<a href="http://creativecommons.org/licenses/by/3.0" target="_blank">http://creativecommons.org/licenses/by/3.0</a>)':
                {'type': 'cc-by', 
                 'version':'3.0', 
                 'url': 'http://creativecommons.org/licenses/by/3.0'}
            },
            {"under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0)":
                {'type': 'cc-nc', 
                 'version':'3.0', 
                 'url': 'http://creativecommons.org/licenses/by-nc/3.0'}
            },
            {"under the terms of the free Open Government License":
                {'type': 'uk-ogl'}
            },
            {"under the Creative Commons CC0 public domain dedication":
                {'type': 'cc-zero'}
            },
            {"under the terms of the Creative Commons Attribution License":
                {'type': 'cc-by'}
            },
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
        work_on = provider.get('url', [])

        # validate the url(s) - don't actually send out network
        # requests, but at least check if the requests library we're
        # using thinks the URL is sane at all by just preparing a
        # Request object
        for url in work_on:
            if self.supports_url(url):
                return True

        return False
    
    def supports_url(self, url):
        req = requests.Request('GET', url)
        try:
            req.prepare()
            return True
        except requests.exceptions.RequestException as e:
            print e
            return False

    def license_detect(self, record):
        
        """
        This should determine the licence conditions of the article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """
        
        lic_statements = self._license_mappings
        
        for url in record.provider_urls:
            if self.supports_url(url):
                self.simple_extract(lic_statements, record, url,
                        first_match=True)
    
    def get_description(self, plugin_name):
        pd = super(UbiquitousPlugin, self).get_description(plugin_name)
        pd.provider_support = "Supports any URL which will respond to an HTTP GET request"
        return pd
    
    
    
