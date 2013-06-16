import requests, json
from time import sleep


def batchtest():
    # get some records from the OCC corpus (this is a test server, address may change)
    r = requests.get('http://92.235.188.179:9200/occ/record/_search?q=journal.name:plos* OR journal.name:bmc*&size=100')

    # get a list of IDs from the records pulled
    # this may be longer than the amount of records, cos records can have more than one ID type
    ids = []
    for rs in r.json().get('hits',{}).get('hits',[]):
        if len(ids) != 1000:
            rec = rs['_source']
            for i in rec.get('identifier',[]):
                if 'type' in i and 'id' in i:
                    if i['type'].lower() in ["doi","pmid"]:
                        ids.append(i['id'])

    # send the list to the OAG service
    # loop it until informed they have all been processed
    while len(ids):
        print len(ids)
        headers = {'content-type': 'application/json'}
        rr = requests.post('http://localhost:5000/lookup/',data=json.dumps(ids), headers=headers)
        rs = rr.json()
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
