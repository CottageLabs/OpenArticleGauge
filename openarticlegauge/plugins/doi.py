import re, requests
from openarticlegauge import plugin, recordmanager, model_exceptions

class DOIPlugin(plugin.Plugin):
    _short_name = "doi"
    __version__ = "0.1"
    
    ## Plugin Overrides ##
    
    def capabilities(self):
        return {
            "type_detect_verify" : True,
            "canonicalise" : ["doi"],
            "detect_provider" : ["doi"],
            "license_detect" : False
        }
    
    def type_detect_verify(self, bibjson_identifier):
        """
        determine if the provided bibjson identifier has a type of "DOI", by
        inspecting first the "type" parameter, and then by looking at the form
        of the id.  If it is a DOI, then verify that it is a valid one.  If it is not
        valid
        
        Add "type" : "doi" to the bibjson_identifier object if so
        """
        # Something is a DOI if the following conditions are fulfilled:
        # - it has the string "10." in it (at the start, if no prefix)
        # - it either has no prefix, info:doi:, doi:, or dx.doi.org or http://dx.doi.org
        
        if bibjson_identifier.has_key("type") and bibjson_identifier["type"] != "doi":
            return
        
        if not bibjson_identifier.has_key("id"):
            return
        
        # interpret the DOI
        rx = "^((http:\/\/){0,1}dx.doi.org/|(http:\/\/){0,1}hdl.handle.net\/|doi:|info:doi:){0,1}(?P<id>10\\..+\/.+)"
        result = re.match(rx, bibjson_identifier["id"])
        
        # validation
        if bibjson_identifier.has_key("type") and bibjson_identifier["type"] == "doi" and result is None:
            # the bibjson identifier asserts that it is a doi, but the regex does not
            # support this assertion, so we raise an exception
            raise model_exceptions.LookupException("identifier asserts it is a DOI, but cannot validate: " + str(bibjson_identifier["id"]))
        
        if result is None:
            # no assertion that this is a DOI, and no confirmation from the regex
            return
        
        # otherwise, this is confirmed as a DOI
        bibjson_identifier["type"] = "doi"
    
    def canonicalise(self, bibjson_identifier):
        """
        create a canonical form of the identifier
        and insert it into the bibjson_identifier['canonical'].  This is of the form doi:10.xxxx
        """
        # only canonicalise DOIs (this function should only ever be called in the right context)
        if bibjson_identifier.has_key("type") and bibjson_identifier["type"] != "doi":
            return
        
        # do we have enough information to canonicalise, raise an error
        if not bibjson_identifier.has_key("id"):
            raise model_exceptions.LookupException("can't canonicalise an identifier without an 'id' property")
        
        canonical = self.canonical_form(bibjson_identifier["id"])
        bibjson_identifier['canonical'] = canonical
    
    def detect_provider(self, record):
        """
        Attempts to detect the provider using a couple of internal methods:
        - DOI range check (currently not implemented)
        - dereference of DOI to provider website
        """
        self.provider_range_lookup(record)
        self.provider_dereference(record)
    
    ## Public Utility/Action Methods ##
    
    def canonical_form(self, doi):
        # interpret the DOI
        rx = "^((http:\/\/){0,1}dx.doi.org/|(http:\/\/){0,1}hdl.handle.net\/|doi:|info:doi:){0,1}(?P<id>10\\..+\/.+)"
        result = re.match(rx, doi)
        
        if result is None:
            raise model_exceptions.LookupException("identifier does not parse as a DOI: " + str(doi))
        
        # the last capture group is the 10.xxxx bit of the DOI
        tendot = result.groups()[-1:][0]
        
        # canonicalised version is just "doi:10.xxxx"
        canonical = "doi:" + tendot
        return canonical
    
    def provider_range_lookup(self, record):
        """
        Check the DOI (if this is a DOI) against a known set of DOI ranges to determine
        the provider.  Populate the record['provider'] field with the relevant doi range
        information.
        
        FIXME: how exactly is doi range lookup relevant to determining the provider?
        
        DOI ranges - maintain a lookup table of DOI ranges/regexes which define the providers
        not necessarily robust, as a publisher may run out of DOIs in their range
        """
        pass

    def provider_dereference(self, record):
        """
        Check the URL that the DOI dereferences to, by taking advantage of the fact that
        DOI lookups use HTTP 303 to redirect you to the resource. Append to the record['provider']['url']
        list with the string which describes the provider (ideally a URI)
        """
        # check that we can actually work on this record
        # - must have an indentifier
        # - must be a doi
        # - must have a canonical form
        if not "identifier" in record:
            return
        
        if not "type" in record["identifier"]:
            return
        
        if record["identifier"]["type"] != "doi":
            return
        
        if not "canonical" in record["identifier"]:
            return
        
        # first construct a dereferenceable doi (prefix it with dx.doi.org)
        canon = record['identifier']['canonical']
        loc = self.dereference(canon)
        
        # either way we are going to copy the doi into the provider object
        recordmanager.record_provider_doi(record, canon)
        
        if loc is None:
            return
        
        # if we find something, record it
        recordmanager.record_provider_url(record, loc)

    def dereference(self, canonical):
        resolvable = "http://dx.doi.org/" + canonical[4:]
        
        # now dereference it and find out the target of the (chain of) 303(s)
        response = requests.get(resolvable)
        return response.url


