import config
import requests, json, logging
from datetime import datetime

log = logging.getLogger(__name__)

def check_archive(identifier):
    """
    Check the archive layer for an object with the given (canonical) identifier,
    which can be found in the bibjson['identifier']['canonical'] field
    
    Return a bibjson record
    """
    
    result = {}
    if config.buffering:
        log.debug("buffering ...")
        # before checking remote, check the redis buffer queue if one is enabled
        result = {} # should update result to the matching record object found on buffer queue if any
        
    if not result:
        # by just making an ID and GETting and POSTing to it, we can do things faster.
        _id = identifier.replace('/','_')
        log.debug("prepared record ID: " + str(_id))
        result = retrieve(_id)
    
    log.debug(identifier + " yielded result from archive: " + str(result))
    return result


def delete(_id):
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/' + _id.replace('/','_')
    log.debug("sending DELETE to " + addr)
    try:
        r = requests.delete(addr)
        log.debug("Index responded with result set: " + r.text)
        return r.json()
    except requests.ConnectionError:
        # we can actually survive for some time without the archive layer, so no need
        # to cause a fatal exceptions
        log.error("ConnectionError attempting to contact index - possibly the archive is down")
        return None


def retrieve(_id):
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/' + _id.replace('/','_')
    log.debug("sending GET query to " + addr)
    try:
        r = requests.get(addr)
        log.debug("Index responded with result set: " + r.text)
        return r.json().get('_source',{})
    except requests.ConnectionError:
        # we can actually survive for some time without the archive layer, so no need
        # to cause a fatal exceptions
        log.error("ConnectionError attempting to contact index - possibly the archive is down")
        return None


def query(q):
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/_search'
    r = requests.post(addr, data=json.dumps(q))
    return r.json()


def store(bibjson):
    """
    Store the provided bibjson record in the archive (overwriting any item which
    has the same canonical identifier)
    """
    
    _check_index() # TODO: this should not happen on every store but on app instantiation.

    for idobj in bibjson.get('identifier',[]):
        if 'canonical' in idobj.keys():
            bibjson['_id'] = idobj['canonical'].replace('/','_')
    bibjson['_last_modified'] = datetime.now().strftime("%Y-%m-%d %H%M")
    
    if config.buffering:
        # append this bibjson record to the buffer somehow
        buf = 'whatever it was plus this new record'
        # if buffer size limit reached or buffer timeout reached
        if False: # change this to proper decision
            _bulk_save('list of the records in the buffer')
            # flush the buffer however that is done
    else:
        # no buffering, just save this one record
        _save(bibjson)


def _save(bibjson):
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/' + bibjson['_id']
    r = requests.post(addr,data=json.dumps(bibjson))
    return r.json()


def _bulk_save(bibjson_list):
    data = ''
    for r in bibjson_list:
        data += json.dumps( {'index':{'_id':r['_id']}} ) + '\n'
        data += json.dumps( r ) + '\n'
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/_bulk'
    r = requests.post(addr, data=data)
    return r.json()

    
# check for an index with proper mapping - if not there, make it.  
def _check_index():
    # check ES is reachable
    test = 'http://' + str( config.es_address ).lstrip('http://').rstrip('/')
    try:
        hi = requests.get(test)
        if hi.status_code != 200:
            print "there is no elasticsearch index available at " + test
    except:
        print "there is no elasticsearch index available at " + test

    # check to see if index exists - in which case it will have a mapping even if it is empty, create if not
    dbaddr = test + '/' + config.es_indexname
    if requests.get(dbaddr + '/_mapping').status_code == 404:
        print "creating the index"
        c = requests.post(dbaddr)
        print c.status_code

    # check for mapping and create one if provided and does not already exist
    # this will automatically create the necessary index type if it is not already there
    if config.es_mapping:
        t = dbaddr + '/' + config.es_indextype + '/' + '_mapping' 
        if requests.get(t).status_code == 404:
            print "putting the index type mapping"
            p = requests.put(t, data=json.dumps(config.es_mapping) )
            print p.status_code

    
