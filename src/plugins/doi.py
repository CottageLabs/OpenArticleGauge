def type_detect_verify(bibjson_identifier):
    """
    determine if the provided bibjson identifier has a type of "DOI", by
    inspecting first the "type" parameter, and then by looking at the form
    of the id.  If it is a DOI, then verify that it is a valid one.
    
    Add "type" : "doi" to the bibjson_identifier object if so
    """
    pass

def canonicalise(record):
    """
    create a canonical form of the identifier in the record['identifier'] field
    and insert it into the record['identifier']['canonical'].  This is of the form doi:10.xxxx
    """
    pass

#####################################################################
def doi_provider(record):
    return "http://www.plos.com/"
