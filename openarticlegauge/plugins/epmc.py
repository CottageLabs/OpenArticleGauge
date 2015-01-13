import re, logging, requests
from openarticlegauge import plugin, models
from lxml import etree
from openarticlegauge.plugins.doi import DOIPlugin
from bs4 import BeautifulSoup
from openarticlegauge import util

log = logging.getLogger(__name__)

class EPMCPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__ = "0.1"
    __desc__ = "Plugin to interpret Europe Pubmed Central IDs"

    _rx = r"^(PMC){0,1}[\d]{5,7}$"
    # Valid: PMC12345, 12345, PMC123456, 123456, PMC1234567, 1234567
    # Invalid: PMC1, 1, 1234, PMC1234, 12345678, PMC12345678, 123456789012345678901234567890, PMC123456789012345678901234567890
    # see https://github.com/CottageLabs/oacwellcome/issues/15#issuecomment-68896793
    
    def capabilities(self):
        return {
            "type_detect_verify" : True,
            "canonicalise" : ["epmc"],
            "detect_provider" : ["epmc"],
            "license_detect" : False
        }
    
    def type_detect_verify(self, record):
        """
        determine if the provided record's bibjson identifier has a type of "EPMC", by
        inspecting first the "type" parameter, and then by looking at the form
        of the id.  If it is a EPMC, then verify that it is a valid one.
        
        Add "type" : "epmc" to the bibjson_identifier object if so
        """
        if record.has_type() and record.identifier_type != "epmc":
            return

        if not record.has_id():
            return

        # not going to .strip() whitespace from both ends of the ID
        # since the pmid and doi plugins don't do it either

        result = re.match(self._rx, record.id)

        # validation
        if record.has_type() and record.identifier_type == "epmc" and result is None:
            # the bibjson identifier asserts that it is a epmc, but the regex does not
            # support this assertion, so we raise an exception
            raise models.LookupException("identifier asserts it is a EPMC, but cannot validate: " + str(record.id))
        
        if result is None:
            # no assertion that this is a EPMC, and no confirmation from the regex
            return

        record.identifier_type = "epmc"

    def canonicalise(self, record):
        """
        create a canonical form of the identifier
        and insert it into the bibjson_identifier['canonical'].  This is of the form epmc:12345678
        """
        id_ = str(record.id)

        if record.has_type() and record.identifier_type != "epmc":
            return
        
        # do we have enough information to canonicalise, raise an error
        if not record.has_id():
            raise models.LookupException("can't canonicalise an identifier without an 'id' property")

        result = re.match(self._rx, record.id)
        if result is None:
            raise models.LookupException("identifier does not parse as a EPMC: " + id_)

        if not id_.startswith('PMC'):
            canonical = 'PMC' + id_
        else:
            canonical = id_

        record.canonical = canonical

    # ET TODO - detect_provider, _scrape_urls and _resolve_doi if applicable

    def detect_provider(self, record):
        """
        Take an EPMC id (if that is the type) and obtain a reference to the base
        URL of the resource that it links to and append it to the record['provider']['url'] list
        """
        # check that we can actually work on this record
        # - must have an indentifier
        # - must be a epmc
        # - must have a canonical form
        if record.identifier_type != "epmc" or record.canonical is None:
            return

        # not the original provider, but enough info and includes the full text
        record.add_provider_url("http://europepmc.org/articles/{epmc_id}".format(epmc_id=record.canonical))

        return
        # in case we want the original provider we should do something similar to the below

        # # see if we can resolve a doi for the item
        # canon = record.canonical
        # doi, loc = self._resolve_doi(canon)
        #
        # if loc is not None:
        #     # if we find something, record it
        #     record.add_provider_url(loc)
        #     record.set_provider_doi(doi)
        #     return
        #
        # # if we get to here, the DOI lookup failed, so we need to scrape the NCBI site for possible urls
        # urls = self._scrape_urls(canon)
        # if urls is not None and len(urls) > 0:
        #     # if we find something, record it
        #     record.add_provider_urls(urls)

    # def _scrape_urls(self, canonical_epmc):
    #     """
    #     return a list of urls which might be a suitable provider from the NCBI page
    #     """
    #     ncbi_url = "http://www.ncbi.nlm.nih.gov/pubmed/" + canonical_epmc[5:]
    #     resp = util.http_get(ncbi_url)
    #     if resp.status_code != 200:
    #         return []
    #
    #     soup = BeautifulSoup(resp.text)
    #
    #     # first look for the canonical link under the "icons" class div
    #     icons = soup.find(class_="icons")
    #     if icons is not None:
    #         anchors = icons.find_all("a")
    #         if len(anchors) > 0:
    #             return [anchors[0]['href']]
    #
    #     # if we don't find an "icons" div, then we need to scrape from the "linkoutlist"
    #     linkout = soup.find_all(class_="linkoutlist")
    #     if len(linkout) == 0:
    #         return []
    #     anchors = linkout[0].find_all("a")
    #     if len(anchors) == 0:
    #         return []
    #
    #     urls = []
    #     for a in anchors:
    #         urls.append(a['href'])
    #     return urls
    #
    # def _resolve_doi(self, canonical_epmc):
    #     canonical_doi = None
    #     loc = None
    #     # TODO use http://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/
    #     return canonical_doi, loc
    

