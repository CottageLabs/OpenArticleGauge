import re, logging, requests
from openarticlegauge import plugin, recordmanager, model_exceptions
from lxml import etree
from openarticlegauge.plugins.doi import DOIPlugin
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

class PMIDPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__ = "0.1"
    
    _rx = "^[\d]{1,8}$"
    
    def type_detect_verify(self, bibjson_identifier):
        """
        determine if the provided bibjson identifier has a type of "PMID", by
        inspecting first the "type" parameter, and then by looking at the form
        of the id.  If it is a PMID, then verify that it is a valid one.
        
        Add "type" : "pmid" to the bibjson_identifier object if so
        
        NOTE: PMIDs could come prefixed with a bunch of URL spaces, but we don't really
        have an exhaustive list of these, so for the time being this method will FAIL
        to identify any PMID which is not just a 1 to 8 digit number
        """
        if bibjson_identifier.has_key("type") and bibjson_identifier["type"] != "pmid":
            return
        
        if not bibjson_identifier.has_key("id"):
            return
        
        # 1 to 8 digits long
        result = re.match(self._rx, bibjson_identifier["id"])
        
        # validation
        if bibjson_identifier.has_key("type") and bibjson_identifier["type"] == "pmid" and result is None:
            # the bibjson identifier asserts that it is a pmid, but the regex does not
            # support this assertion, so we raise an exception
            raise model_exceptions.LookupException("identifier asserts it is a PMID, but cannot validate: " + str(bibjson_identifier["id"]))
        
        if result is None:
            # no assertion that this is a PMID, and no confirmation from the regex
            return
        
        # otherwise, this is confirmed as a PMID
        bibjson_identifier["type"] = "pmid"

    def canonicalise(self, bibjson_identifier):
        """
        create a canonical form of the identifier
        and insert it into the bibjson_identifier['canonical'].  This is of the form pmid:12345678
        """
        # only canonicalise DOIs (this function should only ever be called in the right context)
        if bibjson_identifier.has_key("type") and bibjson_identifier["type"] != "pmid":
            return
        
        # do we have enough information to canonicalise, raise an error
        if not bibjson_identifier.has_key("id"):
            raise model_exceptions.LookupException("can't canonicalise an identifier without an 'id' property")
        
        # 1 to 8 digits long
        result = re.match(self._rx, bibjson_identifier["id"])
        if result is None:
            raise model_exceptions.LookupException("identifier does not parse as a PMID: " + str(bibjson_identifier["id"]))
        
        # no need to validate the ID - we just prefix "pmid:" since there is an id, and the
        # type is indicated as "pmid"
        canonical = "pmid:" + bibjson_identifier['id']
        bibjson_identifier['canonical'] = canonical
        
    def detect_provider(self, record):
        """
        Take a pubmed id (if that is the type) and obtain a reference to the base
        URL of the resource that it links to and append it to the record['provider']['url'] list
        """
        # check that we can actually work on this record
        # - must have an indentifier
        # - must be a pmid
        # - must have a canonical form
        if not "identifier" in record:
            return
        
        if not "type" in record["identifier"]:
            return
        
        if record["identifier"]["type"] != "pmid":
            return
        
        if not "canonical" in record["identifier"]:
            return
        
        # see if we can resolve a doi for the item
        canon = record['identifier']['canonical']
        doi, loc = self._resolve_doi(canon)
        
        if loc is not None:
            # if we find something, record it
            recordmanager.record_provider_url(record, loc)
            recordmanager.record_provider_doi(record, doi)
            return
        
        # if we get to here, the DOI lookup failed, so we need to scrape the NCBI site for possible urls
        urls = self._scrape_urls(canon)
        if urls is not None and len(urls) > 0:
            # if we find something, record it
            recordmanager.record_provider_urls(record, urls)

    def _scrape_urls(self, canonical_pmid):
        """
        return a list of urls which might be a suitable provider from the NCBI page
        """
        ncbi_url = "http://www.ncbi.nlm.nih.gov/pubmed/" + canonical_pmid[5:]
        resp = requests.get(ncbi_url)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text)
        
        # first look for the canonical link under the "icons" class div
        icons = soup.find(class_="icons")
        if icons is not None:
            anchors = icons.find_all("a")
            if len(anchors) > 0:
                return [anchors[0]['href']]
            
        # if we don't find an "icons" div, then we need to scrape from the "linkoutlist"
        linkout = soup.find_all(class_="linkoutlist")
        if len(linkout) == 0:
            return []
        anchors = linkout[0].find_all("a")
        if len(anchors) == 0:
            return []
        
        urls = []
        for a in anchors:
            urls.append(a['href'])
        return urls

    def _resolve_doi(self, canonical_pmid):
        xml_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + canonical_pmid[5:] + "&retmode=xml"
        
        # now dereference it and find out the target of the (chain of) 303(s)
        response = requests.get(xml_url)
        try:
            xml = etree.fromstring(response.text.encode("utf-8"))
        except:
            log.error("Error parsing the XML from " + xml_url)
            return None, None
        
        xp = "/PubmedArticleSet/PubmedArticle/PubmedData/ArticleIdList/ArticleId[@IdType='doi']"
        els = xml.xpath(xp)
        
        if len(els) == 0:
            # we didn't find a DOI
            return None, None
            
        # FIXME: we assume there is only one DOI in the record - is this really true?
        doi_string = els[0].text
        doi = DOIPlugin()
        canonical_doi = doi.canonical_form(doi_string)
        loc = doi.dereference(canonical_doi)
        
        return canonical_doi, loc
    

