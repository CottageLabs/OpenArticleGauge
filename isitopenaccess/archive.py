import config
import requests, json

def check_archive(identifier):
    """
    Check the archive layer for an object with the given (canonical) identifier,
    which can be found in the bibjson['identifier']['canonical'] field
    
    Return a bibjson record
    """
    idtype, idid = identifier.split(':')
    
    result = {}
    if config.bibserver_buffering:
        # before checking remote, check the redis buffer queue if one is enabled
        result = {} # should update result to the matching record object found on buffer queue if any
        
    if not result:
        # query bibserver for this identifier and order by descending last modified
        query = {
            'query':{
                'term':{
                    "identifier.id.exact": identifier
                }
            },
            'sort':{
                
            }
        }

        if config.es_address:
            addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/_search'
        else:
            addr = config.bibserver_address + '/query'

        r = requests.post(addr, data=json.dumps(query))
        results = r.json().get('hits',{}).get('hits',[])
        if len(results) > 0: result = results[0]['_source']
    
    return result
    

def store(bibjson):
    """
    Store the provided bibjson record in the archive (overwriting any item which
    has the same canonical identifier)
    """
    if config.bibserver_buffering:
        # append this bibjson record to the buffer somehow
        buf = 'whatever it was plus this new record'
        # if buffer size limit reached or buffer timeout reached
        if False: # change this to proper decision
            bulk_save('list of the records in the buffer')
            # flush the buffer however that is done
    else:
        # no buffering, just save this one record
        save(bibjson)


def save(bibjson):
    # send one record to bibserver / es
    if config.es_address:
        addr = config.es_address + '/' + config.es_indexname + '/' + config.es_indextype + '/' + bibjson['_id']
    else:
        addr = config.bibserver_address + '/record/' + bibjson['_id'] + '?api_key=' + config.bibserver_api_key

    r = requests.post(addr,data=json.dumps(bibjson))
    return r.json()


def bulk_save(bibjson_list):
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
        pass
    
    
    