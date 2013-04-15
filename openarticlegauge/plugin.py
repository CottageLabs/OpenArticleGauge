from openarticlegauge import config, plugloader, recordmanager
from openarticlegauge.licenses import LICENSES
from openarticlegauge import oa_policy
import logging, requests
from copy import deepcopy
from datetime import datetime

log = logging.getLogger(__name__)

class Plugin(object):
    
    ## Capabilities that must be implemented by the sub-class ##
    __version__ = "0.0"
    _short_name = "vanilla_plugin"
    
    def capabilities(self):
        """
        Describe the capabilities of this plugin, in the following form:
        
        {
            "type_detect_verify" : True,
            "canonicalise" : ["<supported type>"],
            "detect_provider" : ["<supported type>"],
            "license_detect" : True
        }
        
        Omit any key for any feature that the plugin does not support, or set the
        value of the key to False
        """
        return {}
    
    def type_detect_verify(self, bibjson_identifier):
        """
        determine if the provided bibjson identifier has the correct type for this plugin, by
        inspecting first the "type" parameter, and then by looking at the form
        of the id.  If it is tagged as a DOI, then verify that it is a valid one. 
        
        Add "type" parameter to the bibjson_identifier object if successful.
        """
        raise NotImplementedError("type_detect_verify has not been implemented")
    
    def canonicalise(self, bibjson_identifier):
        """
        create a canonical form of the identifier
        and insert it into the bibjson_identifier['canonical'].
        """
        raise NotImplementedError("canonicalise has not been implemented")
        
    def detect_provider(self, record):
        """
        Attempt to determine information regarding the provider of the identifier.
        
        Identifier can be found in record["identifier"].
        
        This function should - if successful - populate the record["provider"] field
        (create if necessary), with any information relevant to downstream plugins
        (see back-end documentation for more information)
        """
        raise NotImplementedError("detect_provider has not been implemented")
        
    def supports(self, provider):
        """
        Does the page_license method in this plugin support this provider
        """
        raise NotImplementedError("supports has not been implemented")
    
    def license_detect(self, record):
        """
        Determine the licence conditions of the record.  Plugins may achieve this by
        any means, although the record['provider']['url'] and record['provider']['doi']
        fields will be key pieces of information.
        
        Plugins should populate (create if necessary) record['bibjson'] and populate with
        a record containing a "license" as per the back-end and API documentation
        """
        raise NotImplementedError("license_detect has not been implemented")
    
    ## utilities that the sub-class can take advantage of ##
    
    def clean_url(self, url):
        # strip any leading http:// or https://
        if url.startswith("http://"):
            url = url[len("http://"):]
        elif url.startswith("https://"):
            url = url[len("https://"):]

        return url

    def clean_urls(self, urls):
        cleaned_urls = []
        for url in urls:
            cleaned_urls.append(self.clean_url(url))
        return cleaned_urls

    def simple_extract(self, lic_statements, record, url):
        """
        Generic code which looks for a particular string in a given web page (URL),
        determines the licence conditions of the article and populates
        the record['bibjson']['license'] (note the US spelling) field.

        The URL it analyses, the statements it looks for and the resulting licenses
        are passed in. This is not a plugin for a particular publisher - it just
        contains (allows re-use) the logic that any "dumb string matching" plugin 
        would use.

        :param handler: The name of the plugin which called this function to
        handle the record.
        :param handler_version: The __version__ of the plugin which called this
        function to handle the record.
        :param lic_statements: licensing statements to look for on this publisher's 
        pages. Take the form of {statement: meaning}
        where meaning['type'] identifies the license (see licenses.py)
        and meaning['version'] identifies the license version (if available)
        See a publisher plugin for an example, e.g. bmc.py
        :param record: a request for the OAG status of an article, see OAG docs for
        more info.
        :param url: source url of the item to be fetched. This is where the HTML
        page that's going to be scraped is expected to reside.
        """

        # get content
        r = requests.get(url)
        
        # see if one of the licensing statements is in content 
        # and populate record with appropriate license info
        for statement_mapping in lic_statements:
            # get the statement string itself - always the first key of the dict
            # mapping statements to licensing info
            statement = statement_mapping.keys()[0]

            #import logging
            #logging.debug('Statement "' + statement + '"...')

            if statement in r.content:
                
                #logging.debug('... matches')

                # okay, statement found on the page -> get license type
                lic_type = statement_mapping[statement]['type']

                # license identified, now use that to construct the license object
                license = deepcopy(LICENSES[lic_type])
                license['open_access'] = oa_policy.oa_for_license(lic_type)
                # set some defaults which have to be there, even if empty
                license.setdefault('version','')
                license.setdefault('description','')
                license.setdefault('jurisdiction','') # TODO later (or later version of OAG!)
                
                # Copy over all information about the license from the license
                # statement mapping. In essence, transfer the knowledge of the 
                # publisher plugin authors to the license object.
                # Consequence: Values coming from the publisher plugin overwrite
                # values specified in the licenses module.
                license.update(statement_mapping[statement])
                
                # add provenance information to the license object
                provenance = {
                    'date': datetime.strftime(datetime.now(), config.date_format),
                    'source': url,
                    'agent': config.agent,
                    'category': 'page_scrape', # TODO we need to think how the
                        # users get to know what the values here mean.. docs?
                    'description': self.gen_provenance_description(url, statement),
                    'handler': self._short_name, # the name of the plugin processing this record
                    'handler_version': self.__version__ # version of the plugin processing this record
                }

                license['provenance'] = provenance

                record['bibjson'].setdefault('license', [])
                record['bibjson']['license'].append(license)

            #logging.debug('... does NOT match')
    
    def gen_provenance_description(self, source_url, statement):
        return 'License decided by scraping the resource at ' + source_url + ' and looking for the following license statement: "' + statement + '".'

    def gen_provenance_description_fail(self, source_url):
        return 'We have found it impossible or prohibitively difficult to decide what the license of this item is by scraping the resource at ' + source_url + '. See "error_message" in the "license" object for more information.'

    def describe_license_fail(self, record, source_url, why, suggested_solution='', licence_url=""):
        recordmanager.add_license(
            record, 
            source=source_url, 
            error_message=why, 
            suggested_solution=suggested_solution, 
            url=licence_url,
            type="failed-to-obtain-license",
            open_access=False,
            category="page_scrape",
            provenance_description=self.gen_provenance_description_fail(source_url),
            handler=self._short_name,
            handler_version=self.__version__
        )

class PluginFactory(object):
    
    @classmethod
    def type_detect_verify(cls):
        # FIXME: this should be updated to utilise the "capabilities" aspect of the plugin
        plugins = []
        for plugin_class in config.type_detection:
            klazz = plugloader.load(plugin_class)
            if klazz is None:
                log.warn("unable to load plugin for detecting identifier type from " + str(plugin_class))
                continue
            plugins.append(klazz()) # append an instance of the class
        return plugins
    
    @classmethod
    def canonicalise(cls, identifier_type):
        plugin_class = config.canonicalisers.get(identifier_type)
        klazz = plugloader.load(plugin_class)
        return klazz() # return an instance of the class
    
    @classmethod
    def detect_provider(cls, identifier_type):
        plugins = []
        for plugin_class in config.provider_detection.get(identifier_type, []):
            # all provider plugins run, until each plugin has had a go at determining provider information
            klazz = plugloader.load(plugin_class)
            plugins.append(klazz()) # append an instance of the class
        return plugins
    
    @classmethod
    def license_detect(cls, provider_record):
        for plugin_class in config.license_detection:
            log.debug("checking " + plugin_class + " for support of provider " + str(provider_record))
            klazz = plugloader.load(plugin_class)
            if klazz is None:
                continue
            inst = klazz()
            
            if inst.supports(provider_record):
                log.debug(plugin_class + " (" + inst._short_name + " v" + inst.__version__ + ") services provider " + str(provider_record))
                return inst
        return None
