## When you're done writing the plugin code, you can remove all comments which
## start with two hash signs (##), leaving the code cleaner and more readable.
## It can easily be done manually, or using regular expression such as
## ^\s*##.* (select everything starting with ##, regardless of indentation)

## ~~ TUTORIAL: YOU NEED TO MODIFY THIS ~~
"""
This plugin handles BioMedCentral articles.
This is an example plugin that should not actually run without modification as
there is a proper BMC plugin as well, which may be more up-to-date.
"""

## We import the plugin module from the openarticlegauge module, as this contains
## essential bits of infrastructure for us to build our plugin on.
from openarticlegauge import plugin

## Create a new class which extends the plugin.Plugin class.  The rest of this
## file shows how to extend and override the methods it provides signatures for
class Tutorial(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin

    # The domains that this plugin will say it can support.
    # Specified without the schema (protocol - e.g. "http://") part.
    ## ~~ TUTORIAL: YOU NEED TO MODIFY THIS ~~
    base_urls = ["www.biomedcentral.com"]
    # so if the http://www.biomedcentral.com/1471-2164/13/425 URL comes in,
    # it should be supported.
    
    ## You can keep the supports() function as it is if your publisher only has
    ## a few domain names and doesn't need anything more special than
    ## "Does this URL start with this domain name?"
    def supports(self, provider):
        """
        Does this plugin support this provider
        """
        
        work_on = self.clean_urls(provider.get("url", []))

        for url in work_on:
            if self.supports_url(url):
                return True

        return False

    ## This is what actually does the analysis on an incoming URL.
    ## You can keep it as-is unless your publisher has many websites, in which case
    ## you might want to match a regex like "^*.mypublisher.com" .
    def supports_url(self, url):
        """
        Same as the supports() function but answers the question for a single URL.
        """
        for bu in self.base_urls:
            if self.clean_url(url).startswith(bu):
                return True
        return False

    ## The function that does the license extraction itself.
    ## You should modify this:
    ## 1. The docstring at the top, stating which provider (publisher) it supports.
    ## 2. The licensing statements: how can the plugin know if a certain license
    ## is in force? You need to define at least one such statement.
    def license_detect(self, record):
        ## ~~ TUTORIAL: YOU NEED TO MODIFY THIS ~~
        """
        To respond to the provider identifier: http://www.biomedcentral.com
        
        This should determine the licence conditions of the BMC article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """

        # licensing statements to look for on this publisher's pages
        # take the form of {statement: meaning}

        ## ~~ TUTORIAL: YOU NEED TO MODIFY THIS ~~
        lic_statements = [
            {"This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.":
                {'type': 'cc-by', # license type, see the licenses module for available ones
                    ## The one thing to be careful about is identifying your license with "type"
                    ## This MUST correspond to one of the objects in the /openarticlegauge/licenses.py
                    ## file. That is based on opendefinition.org . If your license is not present,
                    ## modify the licenses.py file and include it as a new record at the bottom,
                    ## preferably by copying the record of another license and filling in as many
                    ## fields as you can.

                 'version':'2.0', # version of the license if specified, can be blank

                    # also declare some properties which override info about this license in the licenses list (see licenses module)

                    ## The list in the licenses module sometimes has more
                    ## general information - for example, it doesn't link to a
                    ## specific version of the CC-BY license, just the
                    ## opendefinition.org page for it. This plugin knows a better
                    ## URL though, since it's present in the license statement above.
                    'url': 'http://creativecommons.org/licenses/by/2.0'}

                    ## The license rights / requirements are defined centrally in the
                    ## licenses module, not in plugins.
                    ## So the NC, SA and ND fields *must* be defined for this license in
                    ## the licenses module for it to be correctly recognised as open
                    ## access (or not). It's recommended to define BY as well. See the
                    ## licenses module for more information if you do not know what these
                    ## field names mean.

            ## You can have as many license statements as you like! In order to add another license, just add a comma ... 
            }, ## <-- ... right after the closing bracket for the previous license statement ...
            ## ... copy the previous license statement after the comma and edit it!

            ## ~~ TUTORIAL: YOU NEED TO MODIFY THIS ~~
            ## If you don't want more than one license statement for now, just
            ## delete this second statement entirely. It's OK to leave the
            ## comma before it.
            {"This is an open-access article distributed under the terms of the free Open Government License, which permits unrestricted use, distribution and reproduction in any medium, provided the original author and source are credited.":
                {'type': 'uk-ogl'} # license type, see the licenses module for available ones
            } ## Just add a comma here and copy the record again to add a
              ## *third* license statement.
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
