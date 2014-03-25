"""
This plugin matches incoming identifiers to Publisher configurations from the database.

It's a bit special - instead of storing what license statements match to what licenses
in the code, it fetches these (called Publisher configurations) from the database.
"""
from openarticlegauge import plugin
from openarticlegauge.models import Publisher, LicenseStatement

import requests
import json

class GenericStringMatcherPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__ = '0.1' 
    __priority__ = -1000
    
    def has_name(self, plugin_name):
        """
        Return True if there is a configuration for the given plugin name
        """
        r = Publisher.query(q='publisher_name:' + plugin_name.lower())
        if r['hits']['total'] > 0:
            return True
        return False
    
    def get_names(self):
        """
        Return the list of names of configurations supported by the GSM
        """
        configs = Publisher.all()
        names = [p['publisher_name'] for p in configs]
        return names
    
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
        # temporary while this plugin acts as the ubiquitous plugin
        return True
        '''
        work_on = provider.get('url', [])
        work_on = self.clean_urls(work_on)
        work_on = self.get_domain(work_on)

        configs = Publisher.q2obj(terms={'journal_urls':work_on})
        if configs:
            return True

        return False
        '''

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
        configs = Publisher.all()
        names = [p['publisher_name'] for p in configs]

        p = Publisher.q2obj(q='publisher_name:' + plugin_name.lower())
        if not p:
            # shouldn't really happen, but this should give an
            # indication if it does
            raise ValueError('Unsupported plugin name.')
        p = p[0]

        ls = LicenseStatement.all()
        license_support = "The following license statements are recognised:\n\n"
        for license in p.data['licenses']:
            statement = license['license_statement']
            ltype = license['license_type']
            version = license['version']
            license_support += ltype + " " + version + ":\n" + statement   + "\n\n"

        for license in ls:
            statement = license['license_statement']
            ltype = license['license_type']
            version = license.get('version', '')
            license_support += ltype + " " + version + ":\n" + statement   + "\n\n"

        return plugin.PluginDescription(
            name=plugin_name,
            version=self.__version__,
            description="A supported publisher (registered via the register a publisher form)",
            provider_support="\n".join(p.data['journal_urls']),
            license_support=license_support,
            edit_id=p['id']
        )
    
    def license_detect(self, record):
        work_on = record.provider_urls

        '''
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
        '''

        lic_statements = []
        all_statements = LicenseStatement.all()
        for l in all_statements:
            lic_statement = {}
            lic_statement[l['license_statement']] = {'type': l['license_type'], 'version': l['version']}
            lic_statements.append(lic_statement)

        for url in work_on:
            self.simple_extract(lic_statements, record, url, first_match=True)
