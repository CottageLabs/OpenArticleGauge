"""
This plugin matches incoming identifiers to Publisher configurations from the database.

It's a bit special - instead of storing what license statements match to what licenses
in the code, it fetches these (called Publisher configurations) from the database.
"""
from flask import url_for
from openarticlegauge import plugin
from openarticlegauge.models import Publisher, LicenseStatement

from collections import OrderedDict


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
        configs = Publisher.all(sort=[{"publisher_name.exact" : {"order" : "asc"}}])
        names = [p['publisher_name'] for p in configs]
        print names
        return names
    
    def capabilities(self):
        return {
            "type_detect_verify": False,
            "canonicalise": [],
            "detect_provider": [],
            "license_detect": True
        }
    
    def supports(self, provider):
        """
        Does this plugin support this provider - the GSM acts as an
        ubiquitous plugin, attempting a flat list of license statements
        regardless or URL if all other options fail.
        """
        return True
    
    def get_description(self, plugin_name):
        """
        Return a plugin.PluginDescription object that describes the plugin configuration
        identified by the given name
        """

        p = Publisher.q2obj(q='publisher_name:' + plugin_name.lower())
        if not p:
            # shouldn't really happen, but this should give an
            # indication if it does
            raise ValueError('Unsupported plugin name.')
        p = p[0]

        license_support = "The following license statements are recognised:\n\n"
        statement_index = []
        for lic in p.data['licenses']:
            statement = lic['license_statement']
            statement_index.append(statement)
            ltype = lic['license_type']
            version = lic['version']
            license_support += ltype + " " + version + ":\n" + statement + "\n\n"

        return plugin.PluginDescription(
            name=plugin_name,
            version=self.__version__,
            description="A supported publisher (registered via the register a publisher form). If none of the registered license statements results in a match, OAG will try all of the <a href=\"{registered_licenses_url}\">registered license statements</a> too.".format(registered_licenses_url=url_for('license_statement.list_statements')),
            provider_support="\n".join(p.data['journal_urls']),
            license_support=license_support,
            edit_id=p['id']
        )
    
    def license_detect(self, record):
        # get all the URL-s from ES into a list
        #     need some way of getting facets from the DAO, ideally
        #     directly in list form as well as the raw form
        all_configs = Publisher.all(sort=[{'publisher_name': 'asc'}])  # always get them in the same order relative to each other
        url_index = self._generate_publisher_config_index_by_url(all_configs)
        url_index = OrderedDict(sorted(url_index.iteritems(), key=lambda x: len(x[0]), reverse=True))  # longest url-s first
        id_index = self._generate_publisher_config_index_by_id(all_configs)

        # get all the configs that match
        matching_configs = []
        work_on = record.provider_urls
        work_on = self.clean_urls(work_on, strip_leading_www=True)

        for config_url, config_id in url_index.items():
            for incoming_url in work_on:
                if incoming_url.startswith(config_url):
                    matching_configs.append(id_index[config_id])
        # future:
        # use tries to prefix match them to the incoming URL
        #     if the results of this could be ordered by URL length that
        #     would be great, or stop at first match option

        # order their license statements by whether they have a version,
        # and then by length
        matching_configs_licenses = []
        for config in matching_configs:
            matching_configs_licenses += config['licenses']

        matching_configs_licenses = sorted(
            matching_configs_licenses,
            key=lambda lic: (
                lic.get('version'),  # this will actually sort licenses in REVERSE ALPHABETICAL order of their versions, blank versions go last
                len(lic['license_statement'])
            ),
            reverse=True
        )

        # try matching like that
        lic_statements = []
        for l in matching_configs_licenses:
            lic_statement = {}
            lic_statement[l['license_statement']] = {'type': l['license_type'], 'version': l['version']}
            lic_statements.append(lic_statement)

        for incoming_url in record.provider_urls:
            self.simple_extract(lic_statements, record, incoming_url, first_match=True)


        #print record.json(indent=3)

        # if that does not result in a license being found, try the flat list
        lic_statements = []
        if not record.has_license() and not record.was_licensed():
            # didn't manage to find one, time to try the flat list

            all_statements = LicenseStatement.all()
            all_statements = sorted(
                all_statements,
                key=lambda lic: (
                    lic.get('version', '') == '',  # does it NOT have a version? last!
                    # see http://stackoverflow.com/questions/9386501/sorting-in-python-and-empty-strings

                    len(lic['license_statement'])  # length of license statement
                )
            )

            for l in all_statements:
                lic_statement = {}
                lic_statement[l['license_statement']] = {'type': l['license_type'], 'version': l.get('version', '')}
                lic_statements.append(lic_statement)

            for incoming_url in record.provider_urls:
                self.simple_extract(lic_statements, record, incoming_url, first_match=True)

        # FIXME: this won't work properly for the GSM - it needs to return the name and version of the configuration
        # that ran
        return (self._short_name, self.__version__)

    @staticmethod
    def longest_prefix_match(search, urllist):
        matches = [url for url in urllist if url.startswith(search)]
        if matches:
            return max(matches, key=len)
        else:
            return ''

    def _generate_publisher_config_index_by_url(self, all_configs):
        res = {}
        for c in all_configs:
            for url in c['journal_urls']:
                res[self.clean_url(url, strip_leading_www=True)] = c['id']
        return res

    @staticmethod
    def _generate_publisher_config_index_by_id(all_configs):
        res = {}
        for c in all_configs:
            res[c['id']] = c
        return res
