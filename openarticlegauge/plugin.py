"""
Common infrastructure for the plugin framework

"""

from openarticlegauge import config
from openarticlegauge.licenses import LICENSES
from openarticlegauge import oa_policy
from openarticlegauge import util

import logging
from copy import deepcopy
from datetime import datetime
import bleach
import requests

import os, imp, string, re

log = logging.getLogger(__name__)
whitespace_re = re.compile(r'\s+')
html_tag_re = re.compile(r'<.*?>')

class Plugin(object):
    """
    Abstract plugin superclass providing interface and some default implementations
    
    """
    
    ## Capabilities that must be implemented by the sub-class ##
    __version__ = "0.0"
    _short_name = "vanilla_plugin"
    __desc__ = "A description of this plugin"
    __priority__ = 0
    
    ## Capabilities that may be implemented by the sub-class ##
    #
    # if you use these features, then you should use supports_by_base_url
    # as the implementation for your supports method, and the simple_extract
    # method
    #
    _base_urls = []
    _license_mappings = []
    
    def has_name(self, name):
        """
        Determines whether this plugin responds to this name
        """
        return name == self._short_name
    
    def get_names(self):
        return [self._short_name]
    
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
    
    def type_detect_verify(self, record):
        """
        determine if the provided record's bibjson identifier has the correct type for this plugin, by
        inspecting first the "type" parameter, and then by looking at the form
        of the id.  If it is tagged as a DOI, then verify that it is a valid one. 
        
        Add "type" parameter to the record object if successful.
        
        arguments:
        record -- a record object containing a minimum of an "id" parameter
        
        """
        raise NotImplementedError("type_detect_verify has not been implemented")
    
    def canonicalise(self, record):
        """
        create a canonical form of the identifier
        and insert it into the bibjson_identifier['canonical'].
        
        arguments:
        record-- a record object containing a minimum of an "id" parameter and a "type" parameter
        
        """
        raise NotImplementedError("canonicalise has not been implemented")
        
    def detect_provider(self, record):
        """
        Attempt to determine information regarding the provider of the identifier.
        
        Identifier can be found in record["identifier"].
        
        This function should - if successful - populate the record["provider"] field
        (create if necessary), with any information relevant to downstream plugins
        (see back-end documentation for more information)
        
        arguments:
        record -- OAG record object.  See high-level documentation for details on its structure
        
        """
        raise NotImplementedError("detect_provider has not been implemented")
        
    def supports(self, provider):
        """
        Does the page_license method in this plugin support this provider
        
        arguments:
        provider -- provider object, see top-level documentation for details on its structure
        
        """
        raise NotImplementedError("supports has not been implemented")
    
    def license_detect(self, record):
        """
        Determine the licence conditions of the record.  Plugins may achieve this by
        any means, although the record['provider']['url'] and record['provider']['doi']
        fields will be key pieces of information.
        
        Plugins should populate (create if necessary) record['bibjson'] and populate with
        a record containing a "license" as per the back-end and API documentation
        
        arguments:
        record -- OAG record object.  See high-level documentation for details on its structure

        returns
        (name, version) - name and version of plugin as executed during license detection
        """
        raise NotImplementedError("license_detect has not been implemented")
    
    def get_description(self, plugin_name):
        """
        Constructs and returns a description for the plugin or plugin configuration
        identified by the given plugin name.
        
        In most cases the plugin_name will be the same as the _short_name but 
        in other cases, where the plugin has multiple identities, the named plugin
        may be different from the _short_name
        
        This returns a PluginDescription object.
        
        The sub-class should overwrite this method if necessary, although standard
        plugins should not need to.
        """
        
        provider_support = "This plugin supports the following url prefixes:\n\n"
        provider_support += "\n".join(self._base_urls)
        
        license_support = "The following license statements are recognised:\n\n"
        for license in self._license_mappings:
            statement = license.keys()[0]
            ltype = license[statement].get("type", "")
            version = license[statement].get("version", "")
            license_support += ltype + " " + version + ":\n" + statement   + "\n\n"
        
        return PluginDescription(
            name=self._short_name, 
            version=self.__version__, 
            description=self.__desc__,
            provider_support=provider_support,
            license_support=license_support
            )
    
    ## utilities that the sub-class can take advantage of ##
    
    def supports_by_base_url(self, provider):
        """
        is the provider supported based on the base_urls that the class
        is configured with.  If you want to use this as the implementation
        for the supports method, then you should use the _base_url member
        variable to store your base urls.
        """
        for url in provider.get("url", []):
            if self.supports_base_url(url):
                return True

        return False
        
    def supports_base_url(self, url):
        """
        Is the provided url supported in the list in _base_url 
        """
        for bu in self._base_urls:
            if self.clean_url(url).startswith(self.clean_url(bu)):
                return True
        return False
    
    @staticmethod
    def clean_url(url, strip_leading_www=True):
        """
        Cleanup the supplied url so it is suitable for comparison inside plugins
        
        arguments
        url -- the url to be cleaned
        
        """
        # strip any leading http:// or https://
        if url.startswith("http://"):
            url = url[len("http://"):]
        elif url.startswith("https://"):
            url = url[len("https://"):]

        if strip_leading_www:
            if url.startswith('www.'):
                url = url[len('www.'):]

        return url

    def clean_urls(self, urls, strip_leading_www=True):
        """
        Cleanup the supplied urls so they are suitable for comparison inside plugins.
        Just runs clean_url(url) on each url.
        
        arguments:
        urls -- array of urls to be cleaned
        
        """
        cleaned_urls = []
        for url in urls:
            cleaned_urls.append(self.clean_url(url, strip_leading_www=strip_leading_www))
        return cleaned_urls

    def simple_extract(self, lic_statements, record, url, first_match=False, content='', handler='', extra_license=None, extra_provenance=None):
        """
        Generic code which looks for a particular string in a given web
        page (URL), determines the licence conditions of the article and
        populates the record['bibjson']['license'] (note the US
        spelling) field.

        The URL it analyses, the statements it looks for and the
        resulting licenses are passed in. This is not a plugin for a
        particular publisher - it just contains (allows re-use) the
        logic that any "dumb string matching" plugin would use.

        :param lic_statements: licensing statements to look for on this
        publisher's pages. Take the form of {statement: meaning} where
        meaning['type'] identifies the license (see licenses.py) and
        meaning['version'] identifies the license version (if available)
        See a publisher plugin for an example, e.g. bmc.py

        :param record: a request for the OAG status of an article, see
        OAG docs for more info.

        :param url: source url of the item to be fetched. This is where
        the HTML page that's going to be scraped is expected to reside.

        :param first_match: stop trying license statements if one of
        them is found at the target url. By default, this code will try
        out all supplied license statements and simply add multiple
        'license' objects to the record it's been passed. If you want
        "first successful match only" behaviour, set this to True.
        """
        if not handler:
            handler = self._short_name  # can't put it in the method signature above, self is unresolved

        if not extra_license:
            extra_license = {}

        if not extra_provenance:
            extra_provenance = {}

        if not content:
            # get content from the web unless it's being passed into this method
            r, content, source_size = util.http_stream_get(url)
            if r.status_code != requests.codes.ok:
                raise PluginException(PluginException.HTTP, "could not retrieve content from " + url + " - " + str(r.status_code))
        else:
            source_size = len(content)

        content = self.normalise_string(content)

        if not content:
            return
        
        # see if one of the licensing statements is in content 
        # and populate record with appropriate license info
        for statement_mapping in lic_statements:
            # get the statement string itself - always the first key of the dict
            # mapping statements to licensing info
            statement = statement_mapping.keys()[0]

            # use a modified version of the license statement for
            # comparison - one which has been subjected to the same
            # normalisation as the incoming content (whitespace,
            # lowercasing etc.)
            cmp_statement = self.normalise_string(statement)
            # do not try to match empty statements, will always result in a match
            if not cmp_statement:
                continue

            # logging.debug(cmp_statement)

            #content = content.decode('utf-8', errors='replace').encode('utf-8', errors='replace')
            #print 'cmp statement type', type(cmp_statement)
            #print 'content type', type(content)

            #if type(cmp_statement) == unicode:
            #    print 'converting cmp_statement to str'
            #    cmp_statement = cmp_statement.encode('utf-8', 'ignore')
            #if type(content) == unicode:
            #    content = content.encode('utf-8', 'ignore')

            if type(cmp_statement) == str:
                #print 'converting cmp_statement to unicode'
                cmp_statement = cmp_statement.decode('utf-8', 'replace')
            if type(content) == str:
                content = content.decode('utf-8', 'replace')

            #print 'after safeguards'
            #print 'cmp statement type', type(cmp_statement)
            #print 'content type', type(content)

            match = cmp_statement in content

            if not match:
                cmp_statement = self.strip_html(cmp_statement)
                content = self.strip_html(content)
                if cmp_statement:  # if there's anything left of the statement after the html stripping...
                                   # otherwise '' in 'string' == True! so lots of false positives
                    match = cmp_statement in content
                else:
                    continue

            if match:
                # logging.debug('... matches')

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
                    "source_size" : source_size,
                    'agent': config.agent,
                    'category': 'page_scrape', # TODO we need to think how the
                        # users get to know what the values here mean.. docs?
                    'description': self.gen_provenance_description(url, statement),
                    'handler': handler, # the name of the plugin processing this record
                    'handler_version': self.__version__ # version of the plugin processing this record
                }

                license['provenance'] = provenance

                # extra fields / meanings provided by plugins
                license.update(extra_license)
                license['provenance'].update(extra_provenance)

                record.add_license_object(license)
                
                if first_match:
                    break

            # logging.debug('... does NOT match')

    def strip_html(self, html_str):
        #html_tag_re.sub('', html_str)
        return bleach.clean(html_str, tags=[], strip=True, strip_comments=True)

    def strip_special_chars(self, s):
        '''
        Only allow ASCII lower- and uppercase letters + arabic digits.
        As well as the ' ', 1 blank space / interval, ASCII 0x20.
        Note that as a side effect, all other whitespace characters will
        be deleted as well, e.g. newlines \n and \r.
        '''
        if not s:
            return s

        allowed = string.ascii_letters + string.digits + ' '

        return ''.join( c for c in s if  c in allowed ) 
                

    def normalise_whitespace(self, s):
        """
        Reduce 1 or more occurences of whitespace to 1 ' ' blank space,
        ASCII 0x20.
        """
        return whitespace_re.sub(' ', s)

    def normalise_string(self, s, strip=False):
        """
        Normalises whitespace and makes the string lowercase in 1 go.

        :param strip: If True, also strips HTML tags and special
        characters incl. Unicode.
        """
        if not s:
            return s

        if strip:
            s = self.strip_html(s)
            s = self.strip_special_chars(s)

        s = self.normalise_whitespace(s)
        s = s.lower()

        return s
    
    def gen_provenance_description(self, source_url, statement):
        return 'License decided by scraping the resource at ' + source_url + ' and looking for the following license statement: "' + statement + '".'

    def gen_provenance_description_fail(self, source_url):
        return 'We have found it impossible or prohibitively difficult to decide what the license of this item is by scraping the resource at ' + source_url + '. See "error_message" in the "license" object for more information.'

    def describe_license_fail(self, record, source_url, why, suggested_solution='', licence_url="", source_size=""):
        record.add_license(
            source=source_url,
            source_size=source_size,
            error_message=why, 
            suggested_solution=suggested_solution, 
            url=licence_url,
            type="failed-to-obtain-license",
            open_access=False,
            category="page_scrape",
            provenance_description=self.gen_provenance_description_fail(source_url),
            handler=self._short_name, # FIXME: if this gets used elsewhere, these may need to be patched with passable args
            handler_version=self.__version__
        )

class PluginDescription(object):
    def __init__(self, name=None, version=None, description=None, provider_support=None, license_support=None, edit_id=None):
        self.name = name
        self.version = version
        self.description = description
        self.provider_support = provider_support
        self.license_support = license_support
        self.edit_id = edit_id
        

class PluginException(Exception):
    IDENTIFIER = "identifier"
    HTTP = "http"
    DATA = "data"

    def __init__(self, type, message):
        super(PluginException, self).__init__(message)
        self.type = type

class PluginFactory(object):
    
    MODULE_EXTENSIONS = ('.py',) # only interested in .py files, not pyc or pyo
    PLUGIN_CONFIG = None

    @classmethod
    def load_from_directory(cls, plugin_dir=None, klazz=Plugin):
        plugin_dir = plugin_dir if plugin_dir is not None else config.PLUGIN_DIR
        
        # list the plugin modules in the plugin directory
        names = [os.path.splitext(module)[0] 
                    for module in os.listdir(plugin_dir) 
                    if module.endswith(cls.MODULE_EXTENSIONS) and not module.startswith('_')]
        
        # load an instance of each plugin
        plugin_instances = []
        for name in names:
            mod = imp.load_source(name, os.path.join(plugin_dir, name + ".py"))
            members = dir(mod)
            for member in members:
                attr = getattr(mod, member)
                if isinstance(attr, type):
                    if issubclass(attr, klazz):
                        plugin_instances.append(attr())
        
        # for each plugin ask its capabilities, and build the plugin structure
        # from it
        name_register = []
        plugin_structure = {
            "type_detect_verify" : [],
            "canonicalise" : {},
            "detect_provider" : {},
            "license_detect" : [],
            "all" : []
        }
        for inst in plugin_instances:
            # check for name clashes
            names = inst.get_names()
            fail = False
            for name in names:
                if name in name_register:
                    log.warn("Plugin name " + name + " is already registered with the PluginFactory; skipping host plugin")
                    fail = True
            if fail: continue
            name_register += names
            
            # now register the capabilities of the plugin
            caps = inst.capabilities()
            plugin_structure["all"].append(inst)
            if caps.get("type_detect_verify", False):
                plugin_structure["type_detect_verify"].append(inst)
            for t in caps.get("canonicalise", []):
                plugin_structure["canonicalise"][t] = inst
            for t in caps.get("detect_provider", []):
                if t not in plugin_structure["detect_provider"]:
                    plugin_structure["detect_provider"][t] = []
                plugin_structure["detect_provider"][t].append(inst)
            if caps.get("license_detect", False):
                plugin_structure["license_detect"].append(inst)
        
        # finally, sort any lists of plugins in the structure according
        # to their priority
        plugin_structure["all"] = cls._prioritise(plugin_structure.get("all", []))
        plugin_structure["type_detect_verify"] = cls._prioritise(plugin_structure.get("type_detect_verify", []))
        for t in plugin_structure.get("detect_provider", {}):
            plugin_structure["detect_provider"][t] = cls._prioritise(plugin_structure["detect_provider"].get(t, []))
        plugin_structure["license_detect"] = cls._prioritise(plugin_structure.get("license_detect", []))
        
        cls.PLUGIN_CONFIG = plugin_structure

    @classmethod
    def _prioritise(cls, plugin_instances):
        if len(plugin_instances) <= 1:
            return plugin_instances
        
        priorities = []
        lookup = {}
        for inst in plugin_instances:
            priorities.append(inst.__priority__)
            if inst.__priority__ not in lookup:
                lookup[inst.__priority__] = []
            lookup[inst.__priority__].append(inst)
        
        prioritised = []
        priorities = list(set(priorities))
        priorities.sort(reverse=True) # highest to lowest
        for p in priorities:
            insts = lookup[p]
            for inst in insts:
                prioritised.append(inst)
        
        return prioritised

    @classmethod
    def type_detect_verify(cls):
        """
        Load the list of plugins responsible for detecting and verifying the types of identifiers
        
        returns a list of plugin objects (instances, not classes), which all implement the
            plugin.type_detect_verify method
        
        """
        if cls.PLUGIN_CONFIG is None:
            cls.load_from_directory()
        return cls.PLUGIN_CONFIG.get("type_detect_verify", [])
        
    @classmethod
    def canonicalise(cls, identifier_type):
        """
        Load the plugin which is capable of producing canonical versions of the supplied identifier_type
        
        arguments:
        identifier_type -- string representation of the identifier type (e.g. "doi" or "pmid")
        
        returns a plugin object (instance, not class), which implements the plugin.canonicalise method
        
        """
        if cls.PLUGIN_CONFIG is None:
            cls.load_from_directory()
        return cls.PLUGIN_CONFIG.get("canonicalise", {}).get(identifier_type)
        
    @classmethod
    def detect_provider(cls, identifier_type):
        """
        Load the list of plugins which may be responsible for determining the provider for the given
        identifier_type
        
        arguments:
        identifier_type -- string representation of the identifier type (e.g. "doi" or "pmid")
        
        returns a list of plugin objects (instances, not classes), which all implement the
            plugin.detect_provider method
        
        """
        if cls.PLUGIN_CONFIG is None:
            cls.load_from_directory()
        return cls.PLUGIN_CONFIG.get("detect_provider", {}).get(identifier_type, [])
    
    @classmethod
    def license_detect(cls, provider_record):
        """
        Return a plugin which asserts that it is capable of determining the licence type for a
        resource held by the supplied provider
        
        arguments
        provider_record -- an OAG provider record data structure.  See the top-level documentation
            for details on its structure
        
        returns a plugin object (instance, not class) which implements the plugin.license_detect method
        
        """
        if cls.PLUGIN_CONFIG is None:
            cls.load_from_directory()
        
        for inst in cls.PLUGIN_CONFIG.get("license_detect"):
            if inst.supports(provider_record):
                return inst
        return None
    
    @classmethod
    def description(cls, plugin_name):
        """
        Return a plugin description for the current version of the given plugin
        
        arguments
        plugin_name -- the name of the plugin to return a plugin description for
        
        returns a PluginDescription instance
        """
        if cls.PLUGIN_CONFIG is None:
            cls.load_from_directory()
        
        # special treatment for oag default plugin
        if plugin_name == "oag":
            return cls._oag_plugin_description()
        
        for inst in cls.PLUGIN_CONFIG.get("all"):
            if inst.has_name(plugin_name):
                description = inst.get_description(plugin_name)
                return description

    @classmethod
    def list_plugins(cls, category=None, sort_for_display=False):
        if cls.PLUGIN_CONFIG is None:
            cls.load_from_directory()
        
        descriptions = []
        
        instances = []
        if category is None:
            instances = cls.PLUGIN_CONFIG.get("all", [])
        elif category == "license_detect":
            instances = cls.PLUGIN_CONFIG.get("license_detect", [])

        if sort_for_display:
            # plugins with multiple configs first, they won't be affected by the
            # _short_name condition (it's the same on all their instances)
            # then sort by short name
            instances.sort(key=lambda x: (-len(x.get_names()), getattr(x, '_short_name', '')))

        for inst in instances:
            names = inst.get_names()
            for name in names:
                descriptions.append(inst.get_description(name))
        
        return descriptions
    
    @classmethod
    def _oag_plugin_description(cls):
        return PluginDescription(
            name="oag",
            version="0.0",
            description="The OpenArticleGauge default plugin - it runs when no other will",
            provider_support="All providers and URLs are supported",
            license_support="This plugin cannot detect any licences, it will simply record a failure on behalf of all the plugins that wouldn't run.",
        )


