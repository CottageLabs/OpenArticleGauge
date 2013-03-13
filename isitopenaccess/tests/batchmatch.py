import requests, json
from time import sleep


def batchtest():
    # get some records from the OCC corpus (this is a test server, address may change)
    r = requests.get('http://129.67.24.26:9200/test/record/_search?q=journal.name:plos* OR journal.name:bmc*&from=50&size=10000')

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

    # send the list to the IIOA service
    # loop it until informed they have all been processed
    errors = open('errors','w')
    count = 0
    err = 0
    for _id in ids:
        count += 1
        if len(_id) < 9:
            sub = 'pmid:'
        else:
            sub = 'doi:'
        rr = requests.get('http://test.cottagelabs.com:9200/iioa/record/' + sub + _id.replace('/','_'))
        rs = rr.status_code
        #print _id, rs
        if rs != 200:
            err += 1
            errors.write(str(count) + ' ' + str(err) + ' ' + str(_id) + ' ' + str(rs))
    
    errors.close()
    
# run and time it
if __name__ == "__main__":
    from datetime import datetime
    started = datetime.now()
    print started
    batchtest()
    ended = datetime.now()
    print ended
    print ended - started
