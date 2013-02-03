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

def provider_range_lookup(record):
    """
    Check the DOI (if this is a DOI) against a known set of DOI ranges to determine
    the provider.  Populate the record['provider'] field with the string which describes
    the provider (ideally a URI)
    
    DOI ranges - maintain a lookup table of DOI ranges/regexes which define the providers
    not necessarily robust, as a publisher may run out of DOIs in their range
    """
    pass

def provider_dereference(record):
    """
    Check the URL that the DOI dereferences to, by taking advantage of the fact that
    DOI lookups use HTTP 303 to redirect you to the resource. Populate the record['provider'] 
    field with the string which describes the provider (ideally a URI)
    """
    pass
