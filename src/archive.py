def check_archive(identifier):
    """
    Check the archive layer for an object with the given (canonical) identifier,
    which can be found in the bibjson['identifier']['canonical'] field
    
    Return a bibjson record
    """
    pass
    
def store(bibjson):
    """
    Store the provided bibjson record in the archive (overwriting any item which
    has the same canonical identifier)
    """
    pass
