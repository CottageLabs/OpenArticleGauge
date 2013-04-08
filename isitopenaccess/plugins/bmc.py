from isitopenaccess import plugin

class BMCPlugin(plugin.Plugin):
    _short_name = "bmc"
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin
    
    base_urls = ["www.biomedcentral.com"]
    
    ## Plugin parent class overrides ##
    
    def supports(self, provider):
        """
        Does the page_license plugin support this provider
        """    
        work_on = self.clean_urls(provider.get("url", []))

        for url in work_on:
            if self.supports_url(url):
                return True

        return False
    
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
        lic_statements = [
            {
                "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited." : 
                {
                    'type': 'cc-by', 
                    'version':'2.0', 
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by/2.0'
                }
            }
        ]
        
        if "provider" not in record:
            return
        if "url" not in record["provider"]:
            return
        
        for url in record['provider']['url']:
            if self.supports_url(url):
                self.simple_extract(lic_statements, record, url)
    
    ## public utility/action methods ##
    
    def supports_url(self, url):
        for bu in self.base_urls:
            if self.clean_url(url).startswith(bu):
                return True
        return False


