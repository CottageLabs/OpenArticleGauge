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
    # FIXME: this makes an assumption about the form of the canonical identifier
    # and is therefore unreliable.  The search should look in the 
    # bibjson['identifier']['canonical'] field as specified above
    idtype, idid = identifier.split(':',1)
    
    result = {}
    if config.bibserver_buffering:
        log.debug("Bibserver buffering ...")
        # before checking remote, check the redis buffer queue if one is enabled
        result = {} # should update result to the matching record object found on buffer queue if any
        
    if not result:
        # query bibserver for this identifier and order by descending last modified
        query = {
            'query':{
                'bool':{
                    'must':[
                        {
                            'term':{
                               "identifier.type.exact": idtype
                            }
                        },
                        {
                            'term':{
                               "identifier.id.exact": idid
                            }
                        }
                    ]
                }
            },
            'sort':{
                '_last_modified.exact':{
                    'order':'descending'
                }
            }
        }
        log.debug("prepared search query: " + str(query))

        if config.es_address:
            addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/_search'
        else:
            addr = config.bibserver_address + '/query'
        
        log.debug("sending search query to " + addr)
        try:
            r = requests.post(addr, data=json.dumps(query))
        except requests.ConnectionError:
            # we can actually survive for some time without the archive layer, so no need
            # to cause a fatal exceptions
            log.error("ConnectionError attempting to contact BibServer - possibly the archive is down")
            return None
            
        if r.status_code == 500:
            log.debug("Bibserver responded with HTTP code 500; retrying without 'sort' query parameter...")
            del query['sort']
            r = requests.post(addr, data=json.dumps(query))
        log.debug("Bibserver responded with result set: " + r.text)
        results = r.json().get('hits',{}).get('hits',[])
        if len(results) > 0: result = results[0]['_source']
    
    log.debug(identifier + " yielded result from archive: " + str(result))
    return result
    

def store(bibjson):
    """
    Store the provided bibjson record in the archive (overwriting any item which
    has the same canonical identifier)
    """
    
    bibjson['_last_modified'] = datetime.now().strftime("%Y-%m-%d %H%M")
    
    if config.bibserver_buffering:
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
    # send one record to bibserver / es
    if config.es_address:
        addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/' + bibjson['_id']
    else:
        addr = config.bibserver_address + '/record/' + bibjson['_id'] + '?api_key=' + config.bibserver_api_key
    
    r = requests.post(addr,data=json.dumps(bibjson))
    return r.json()


def _bulk_save(bibjson_list):
    # send a batch of bibjson records to bibserver / es
    if config.es_address:
        data = ''
        for r in bibjson_list:
            data += json.dumps( {'index':{'_id':r['_id']}} ) + '\n'
            data += json.dumps( r ) + '\n'
        addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/_bulk'
        r = requests.post(addr, data=data)
        return r.json()
    else:
        # there is no bibserver batch endpoint yet. will add very soon then update this.
        for item in bibjson_list:
            return _save(item)
    
    
    
