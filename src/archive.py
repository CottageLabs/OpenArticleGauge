import requests, json

# I see you have a bunch of config...
# Flask has a whole way of dealing with this but it is not in bens original code at all
# Does it matter? Where would you want these config vars put if not?
bibserver_query_address = 'http://bibsoup.net/query'
bibserver_api_key = '' # should be a real api key for the targeted instance
bibserver_collection = 'isitopenaccess' # collection name that we will put IIOA files into

def check_archive(identifier):
    """
    Check the archive layer for an object with the given identifier.
    
    Return a bibjson record
    """
    query = {} # Need to finish this to be a proper query object

    r = requests.post(bibserver_query_address, data=json.dumps(query))
    results = r.json().get('hits',{}).get('hits',[])

    if len(results) > 0:
        return results[0]['url'] # what do you want back here? The url of the first found record?
    else:
        return False
    
def store(bibjson):
    """
    Store the provided bibjson record in the archive
    """

    # are you only going to send one record at a time?
    # will there be any need to bulk save? - does your processing pipeline allow for a batch to be sent at once?
    # if you are sending 1000's to the bibserver very quickly it could fail a bit
    pass
    
    
    
    
