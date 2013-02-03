import re
import models

def type_detect_verify(bibjson_identifier):
    """
    determine if the provided bibjson identifier has a type of "PMID", by
    inspecting first the "type" parameter, and then by looking at the form
    of the id.  If it is a PMID, then verify that it is a valid one.
    
    Add "type" : "pmid" to the bibjson_identifier object if so
    
    NOTE: PMIDs could come prefixed with a bunch of URL spaces, but we don't really
    have an exhaustive list of these, so for the time being this method will FAIL
    to identify any PMID which is not just an 8 digit number
    """
    if bibjson_identifier.has_key("type") and bibjson_identifier["type"] != "pmid":
        return
    
    if not bibjson_identifier.has_key("id"):
        return
    
    # 8 digits long
    rx = "^[\d]{8}$"
    result = re.match(rx, bibjson_identifier["id"])
    
    # validation
    if bibjson_identifier.has_key("type") and bibjson_identifier["type"] == "pmid" and result is None:
        # the bibjson identifier asserts that it is a pmid, but the regex does not
        # support this assertion, so we raise an exception
        raise models.LookupException("identifier asserts it is a PMID, but cannot validate: " + str(bibjson_identifier["id"]))
    
    if result is None:
        # no assertion that this is a PMID, and no confirmation from the regex
        return
    
    # otherwise, this is confirmed as a PMID
    bibjson_identifier["type"] = "pmid"

def canonicalise(record):
    """
    create a canonical form of the identifier in the record['identifier'] field
    and insert it into the record['identifier']['canonical'].  This is of the form pmid:12345678
    """
    pass
    
def provider_resolver(record):
    """
    Take a pubmed id (if that is the type) and obtain a reference to the base
    URL of the resource that it links to.
    """
    pass
