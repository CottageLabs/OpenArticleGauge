





"""
This plugin handles Copernicus Publications articles.
"""



from openarticlegauge import plugin



class COPERNICUSPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' 
                    

    
    
    
    base_urls = ["www.atmos-chem-phys.net"]
    
    
    
    
    
    
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
        To respond to the provider identifier: http://atmos-chem-phys.net
        
        This should determine the licence conditions of the ACP article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """

        
        

        
        lic_statements = [
            {"under the Creative Commons Attribution 3.0 License":
                {'type': 'cc-by', 
                    
                    
                    
                    
                    
                    

                 'version':'3.0', 

                    

                    
                    
                    
                    
                    
                    'url': 'http://creativecommons.org/licenses/by/3.0'}

                    
                    
                    
                    
                    
                    
                    

            
            }
        ]
        
        
        if "provider" not in record:
            return
        if "url" not in record["provider"]:
            return
        
        
        for url in record['provider']['url']:
            
            if self.supports_url(url):
                self.simple_extract(lic_statements, record, url)
