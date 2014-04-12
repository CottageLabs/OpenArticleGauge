from openarticlegauge import plugin, config
from openarticlegauge.licenses import LICENSES
from openarticlegauge import oa_policy
import requests, logging
from lxml import etree
from copy import deepcopy
from datetime import datetime

log = logging.getLogger(__name__)

class ScienceDirectPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin
    # The long lines in the description below are intentional, as it will be displayed as-is
    # including the whitespace, on a few HTML pages - so newlines *will* show up and look
    # strange. Better let browsers do the word wrapping.
    __desc__ = \
"""Extracts licence information from the Science Direct API.

This plugin will look for the following in the XML response from Elsevier's API:
1. look for the "openaccessArticle" XML element and check its text value is "true"
2. look for the "openaccessUserLicense" XML element and try to extract the license info.
    If it's a link to the creativecommons.org website, the license type is encoded in the URL.

If Elsevier's API says the article's Open Access but doesn't (clearly or at all) say what the license is, we degrade the license to free-to-read."""
    
    _base_urls = ["www.sciencedirect.com"]
    
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : True
        }
    
    def supports(self, provider):
        """
        Does the license_detect plugin support this provider
        """
        return self.supports_by_base_url(provider)
    
    def license_detect(self, record):
        # 1. get DOI from record object
        # doi = record['provider'].get('doi')
        doi = record.provider_doi  # it MUST HAVE the canonical DOI prefix, "doi:" or "DOI:"

        if doi:
        # 2. query Elsevier XML api
            url = 'http://api.elsevier.com/content/article/' + doi
            response = requests.get(url)

            # determine the size of the request
            # (we ignore the content-length header, and just always use the number of bytes that we
            # calculate ourselves)
            source_size = len(bytes(response.content))

            response.encoding = 'utf-8'
            content = response.text
            if type(content) == str:
                content = content.decode('utf-8', 'replace')
            
            try:
                xml = etree.fromstring(content)
            except Exception as e:
                log.error("Error parsing the XML from " + url)
                log.error(e)
                return None  # no point in doing anything else, so just do what
                             # Python would do anyway upon reaching the end of this function
        
            # process the XML response
            namespaces = {'elsevierapi': 'http://www.elsevier.com/xml/svapi/article/dtd'}

            # is it open access at all?
            # case insensitive search for the value "true" in the relevant element
            xpath_oa = "//elsevierapi:openaccessArticle//text()[contains(translate(., 'EURT', 'eurt'), 'true')]"
            it_is_oa = len(xml.xpath(xpath_oa, namespaces=namespaces)) > 0

            # now try to get the license too
            lic_type = None
            lic_version = None
            url_to_record = None

            xpath_license_extract = '//elsevierapi:openaccessUserLicense'
            elements = xml.xpath(xpath_license_extract, namespaces=namespaces)
            if len(elements) > 0:
                license_url = elements[0].text

                if license_url:
                    cleaned_license_url = self.clean_url(license_url)

                    urlparts = cleaned_license_url.split('/')
                    if urlparts[0] == 'creativecommons.org':
                        try:
                            lic_type = 'cc-' + urlparts[2]
                            # if we get to here we know what the license is, i.e. "a success"
                            # so we can use the URL *they* specified
                            url_to_record = license_url
                            try:
                                lic_version = urlparts[3]
                            except IndexError:
                                # we know which CC license but don't know which version
                                # that's OK, just don't assert a version when creating
                                # the license record below
                                pass
                        except IndexError:
                            # it is a creative commons URL, but we can't find the license type part
                            # so it's of no use .. all that's left is to slap free-to-read on it
                            # if Elsevier says the article's OA
                            if it_is_oa:
                                lic_type = 'free-to-read'

            if it_is_oa and not lic_type:
                # Elsevier says the article's OA but we could not determine a license at all
                lic_type = 'free-to-read'

            meaning = {}
            if lic_type:
                meaning['type'] = lic_type
            if lic_version:
                meaning['version'] = lic_version
            if url_to_record:
                meaning['url'] = url_to_record

            if lic_type:
                # license identified, now use that to construct the license object
                license = deepcopy(LICENSES[lic_type])
                license['open_access'] = oa_policy.oa_for_license(lic_type)
                # set some defaults which have to be there, even if empty
                license.setdefault('version','')
                license.setdefault('description','')
                license.setdefault('jurisdiction','')

                # Copy over all information about the license from the license
                # statement mapping. In essence, transfer the knowledge of the
                # publisher plugin authors to the license object.
                # Consequence: Values coming from the publisher plugin overwrite
                # values specified in the licenses module.
                license.update(meaning)

                # add provenance information to the license object
                provenance = {
                    'handler': self._short_name,
                    'handler_version': self.__version__,
                    'date': datetime.strftime(datetime.now(), config.date_format),
                    'source': url,
                    "source_size" : source_size,
                    'agent': config.agent,
                    'category': 'xml_api', # TODO we need to think how the
                        # users get to know what the values here mean.. docs?
                    'description': 'License decided by querying the Elsevier XML API at ' + url
                }

                license['provenance'] = provenance
                record.add_license_object(license)
            else:
                # this plugin failed, but would like to give another plugin the opportunity to try
                # like the Generic String Matcher, for example
                raise plugin.TryAnotherPluginException()