import config
import requests, json, logging
from datetime import datetime

log = logging.getLogger(__name__)


def delete(_id):
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_disputetype + '/' + _id.replace('/','_')
    log.debug("sending DELETE of dispute to " + addr)
    try:
        r = requests.delete(addr)
        log.debug("Index responded to delete with result set: " + r.text)
        # should maybe remove any tag on relevant record to say it is no longer disputed
        return r.json()
    except requests.ConnectionError:
        # we can actually survive for some time without the archive layer, so no need
        # to cause a fatal exceptions
        log.error("ConnectionError attempting to contact index - possibly the archive is down")
        return None


def retrieve(_id):
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_disputetype + '/' + _id.replace('/','_')
    log.debug("sending GET query for dispute to " + addr)
    try:
        r = requests.get(addr)
        log.debug("Dispute index responded to retrieve with result set: " + r.text)
        return r.json().get('_source', {})
    except requests.ConnectionError:
        # we can actually survive for some time without the archive layer, so no need
        # to cause a fatal exceptions
        log.error("ConnectionError attempting to contact index - possibly the archive is down")
        return None


def query(q):
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_disputetype + '/_search'
    log.debug("Querying dispute index with query " + json.dumps(q))
    r = requests.post(addr, data=json.dumps(q))
    log.debug("Dispute index responded to query with result set: " + r.text)
    return r.json()


def new(dispute):
    # do some other stuff for new disputes
    return save(dispute)


def save(dispute):
    _check_index() # TODO: this should not happen on every store but on app instantiation.
    dispute['_last_modified'] = datetime.now().strftime("%Y-%m-%d %H%M")
    addr = config.es_address + '/' + config.es_indexname + '/' + config.es_disputetype + '/' + dispute['_id']
    log.debug("Saving dispute to index: " + json.dumps(bibjson))
    r = requests.post(addr,data=json.dumps(bibjson))
    log.debug("Index responded to dispute save with " + json.dumps(r.json()))
    # should maybe add a tag on the relevant record to say it is disputed
    return r.json()


# check for an index with proper mapping - if not there, make it.  
def _check_index():
    # check ES is reachable
    test = 'http://' + str( config.es_address ).lstrip('http://').rstrip('/')
    try:
        hi = requests.get(test)
        if hi.status_code != 200:
            log.debug("there is no elasticsearch index available at " + test)
    except:
        log.debug("there is no elasticsearch index available at " + test)

    # check to see if index exists - in which case it will have a mapping even if it is empty, create if not
    dbaddr = test + '/' + config.es_indexname
    if requests.get(dbaddr + '/_mapping').status_code == 404:
        log.debug("creating the index")
        c = requests.post(dbaddr)
        log.debug(c.status_code)

    # check for mapping and create one if provided and does not already exist
    # this will automatically create the necessary index type if it is not already there
    if config.es_mapping:
        t = dbaddr + '/' + config.es_indextype + '/' + '_mapping' 
        if requests.get(t).status_code == 404:
            log.debug("PUTting the index type mapping")
            p = requests.put(t, data=json.dumps(config.es_mapping) )
            log.debug(p.status_code)

    
