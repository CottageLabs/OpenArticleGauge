import requests, json

# I see you have a bunch of config...
# Flask has a whole way of dealing with this but it is not in bens original code at all
# Does it matter? Where would you want these config vars put if not?
bibserver_query_address = 'http://bibsoup.net/query'
bibserver_api_key = '' # should be a real api key for the targeted instance
bibserver_collection = 'isitopenaccess' # collection name that we will put IIOA files into

def check_archive(identifier):
    """
    Check the archive layer for an object with the given (canonical) identifier,
    which can be found in the bibjson['identifier']['canonical'] field
    
    Return a bibjson record
    """
    
    # before checking remote, check the redis store buffer queue
    
    # this identifier passed in is going to be the canonical iioa one like doi:10.1245/17476384
    query = {} # Need to finish this to be a proper query object - order by descending last modified

    r = requests.post(bibserver_query_address, data=json.dumps(query))
    results = r.json().get('hits',{}).get('hits',[])

    if len(results) > 0:
        return results[0]['url'] # what do you want back here? The full bibjson object of the first result
    else:
        return False
    
def store(bibjson):
    """
    Store the provided bibjson record in the archive (overwriting any item which
    has the same canonical identifier)
    """

    # are you only going to send one record at a time? - YES
    pass


def bulk_store(bibjson_list):
    # write this as a store on a redis queue that then bulk loads after CONFIG time or CONFIG files
    pass
    
    
    
    
