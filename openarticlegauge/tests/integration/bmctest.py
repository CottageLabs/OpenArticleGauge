import requests, json
from time import sleep


def batchtest():

    idtypes = ["doi"]
    size = 1000

    # get some records from the OCC corpus (this is a test server, address may change)
    addr = 'http://92.235.188.179:9200/occ/record/_search?q=identifier.id:*10.1186*%20AND%20identifier.type.exact:doi%20AND%20*biomed*&size=' + str(size) + '&from='

    _from = 0

    t = requests.get(addr + str(_from))

    total = t.json().get('hits',{}).get('total',0)

    # get a list of IDs from the records pulled
    # this may be longer than the amount of records, cos records can have more than one ID type
    while _from < total:
        r = requests.get(addr + str(_from))
        _from += size
        ids = []
        for rs in r.json().get('hits',{}).get('hits',[]):
            if len(ids) != 1000:
                rec = rs['_source']
                for i in rec.get('identifier',[]):
                    if 'type' in i and 'id' in i:
                        if i['type'].lower() in idtypes:
                            ids.append(i['id'])

        # send the list to the OAG service
        # loop it until informed they have all been processed
        while len(ids):
            print len(ids)
            headers = {'content-type': 'application/json'}
            rr = requests.post('http://oag.cottagelabs.com/lookup/',data=json.dumps(ids), headers=headers)
            rs = rr.json()
            print json.dumps(rs,indent=4)
            if len(rs['processing']) == 0:
                return
            else:
                # strip found from ids and wait then try again
                ids = []
                for p in rs['processing']:
                    ids.append(p['identifier']['id']);
                sleep(2)
    
    
# run and time it
if __name__ == "__main__":
    from datetime import datetime
    started = datetime.now()
    print started
    batchtest()
    ended = datetime.now()
    print ended
    print ended - started
