import requests, json
from time import sleep
from openarticlegauge import config


def bmctest():

    idtypes = ["doi"]
    size = 1000
    wait = False

    # get some records from the OCC corpus
    # http://test.cottagelabs.com:9200
    addr = 'http://test.cottagelabs.com:9200/occ/record/_search?q=identifier.id:*10.1186*%20AND%20identifier.type.exact:doi%20AND%20*biomed*&size=' + str(size) + '&from='

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
            rec = rs['_source']
            for i in rec.get('identifier',[]):
                if 'type' in i and 'id' in i:
                    if i['type'].lower() in idtypes:
                        ids.append(i['id'])

        # send the ID list to the OAG service 1000 at a time
        # loop it until informed they have all been processed
        while len(ids) >= 1000:
            if len(ids) < 1000:
                idbatch = ids[0:len(ids)-1]
                ids = []
            else:
                idbatch = ids[0:999]
                ids = ids[1000:]
            while len(idbatch):
                headers = {'content-type': 'application/json'}
                rr = requests.post('http://{host}:5000/lookup/'.format(host=config.DEFAULT_HOST),data=json.dumps(idbatch), headers=headers)
                rs = rr.json()
                if len(rs['processing']) == 0:
                    return
                else:
                    idbatch = []
                    # if waiting for confirmation they are all processed, add the processing ones back to the ID list
                    # otherwise the empty list sends the loop onto the next batch
                    if wait:
                        for p in rs['processing']:
                            idbatch.append(p['identifier']['id'])
                        sleep(2)
    
    
# run and time it
if __name__ == "__main__":
    from datetime import datetime
    started = datetime.now()
    print started
    bmctest()
    ended = datetime.now()
    print ended
    print ended - started
