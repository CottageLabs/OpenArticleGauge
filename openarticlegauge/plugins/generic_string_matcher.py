"""
This plugin matches incoming identifiers to Publisher configurations from the database.

It's a bit special - instead of storing what license statements match to what licenses
in the code, it fetches these (called Publisher configurations) from the database.
"""
from openarticlegauge import plugin
from openarticlegauge.models import Publisher

import requests
import json

class GenericStringMatcherPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' 
    __priority__ = -1000
    
    def has_name(self, plugin_name):
        """
        Return true if there is a configuration for the given plugin name
        """
        return self._short_name
    
    def get_names(self):
        """
        Return the list of names of configurations supported by the GSM
        """
        return []
    
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
        work_on = self.clean_urls(work_on)
        work_on = self.get_domain(work_on)

        configs = Publisher.q2obj(terms={'journal_urls':work_on})
        if configs:
            return True

        return False

    def get_domain(self, urls):
        res = []
        for url in urls:
            r = url.split('/')[0]
            res.append(r)
        return res
    
    def get_description(self, plugin_name):
        """
        Return a plugin.PluginDescription object that describes the plugin configuration
        identified by the given name
        """
        return plugin.PluginDescription(
            name=plugin_name,
            version=self.__version__,
            description="Some Description",
            provider_support="<list of provider urls>",
            license_support="<list of license statements>",
            edit_id=None # put the configuration's id here, so we can link to the edit page
        )
    
    def license_detect(self, record):
        work_on = record.provider_urls
        config_search = self.clean_urls(work_on)
        
        for index, url in enumerate(config_search):
            config_search[index] = url.split('/')[0]

        configs = Publisher.q2obj(terms={'journal_urls':config_search})

        lic_statements = []
        for c in configs:
            for l in c['licenses']:
                lic_statement = {}
                lic_statement[l['license_statement']] = {'type': l['license_type'], 'version': l['version']}
                lic_statements.append(lic_statement)

        for url in work_on:
            self.simple_extract(lic_statements, record, url, first_match=True)