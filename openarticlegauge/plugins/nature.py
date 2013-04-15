"""
This plugin handles Nature articles, including Scientific Reports and Nature Communications
"""

from openarticlegauge import plugin

class NaturePlugin(plugin.Plugin):
    _short_name = "nature"
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin

    # The domains that this plugin will say it can support.
    # Specified without the schema (protocol - e.g. "http://") part.
    base_urls = ["www.nature.com/"]
    
    # so if the http://www.nature.com/ncomms/journal/v1/n1/full/ncomms1007.html URL comes in,
    # it should be supported.
    
    def supports(self, provider):
        """
        Does this plugin support this provider
        """
        
        work_on = self.clean_urls(provider.get("url", []))

        for url in work_on:
            if self.supports_url(url):
                return True

        return False

    def supports_url(self, url):
        """
        Same as the supports() function but answers the question for a single URL.
        """
        for bu in self.base_urls:
            if self.clean_url(url).startswith(bu):
                return True
        return False

    def license_detect(self, record):        
        """
        To respond to the provider identifier: http://www.nature.com/
        
        This should determine the licence conditions of the Nature article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """

        # licensing statements to look for on this publisher's pages
        # take the form of {statement: meaning}

        ## ~~ TUTORIAL: YOU NEED TO MODIFY THIS ~~
        lic_statements = [
            {'This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License. To view a copy of this license, visit  <a href="http://creativecommons.org/licenses/by-nc-sa/3.0/">http://creativecommons.org/licenses/by-nc-sa/3.0/</a>':
                {'type': 'cc-nc-sa', # license type, see the licenses module for available ones
                         'version':'3.0', # version of the license if specified, can be blank
                         'url': 'http://creativecommons.org/licenses/by-nc-sa/3.0/'}
            },
            {'This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of this license, visit  <a href="http://creativecommons.org/licenses/by-nc-nd/3.0/">http://creativecommons.org/licenses/by-nc-nd/3.0/</a>':
                {'type': 'cc-nc-nd', # license type, see the licenses module for available ones
                         'version':'3.0', # version of the license if specified, can be blank
                         'url': 'http://creativecommons.org/licenses/by-nc-nd/3.0/'}
            },             
            {'This work is licensed under a Creative Commons Attribution 3.0 Unported License. To view a copy of this license, visit  <a href="http://creativecommons.org/licenses/by/3.0/">http://creativecommons.org/licenses/by/3.0/</a>':
                {'type': 'cc-by', # license type, see the licenses module for available ones
                         'version':'3.0', # version of the license if specified, can be blank
                         'url': 'http://creativecommons.org/licenses/by/3.0/'}
            } 
        ]
        
        # some basic protection against missing fields in the incoming record
        if "provider" not in record:
            return
        if "url" not in record["provider"]:
            return
        
        # For all URL-s associated with this resource...
        for url in record['provider']['url']:
            # ... run the dumb string matcher if the URL is supported.
            if self.supports_url(url):
                self.simple_extract(lic_statements, record, url)
