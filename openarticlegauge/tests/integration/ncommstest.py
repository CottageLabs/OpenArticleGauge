import requests, json
from time import sleep


def ncommstest():

    wait = False

    # read in the ncomms list
    n = json.load(open('ncomms.json','r'))
    ids = []
    for o in n:
        ids.append(o['doi'])

    total = len(ids)

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
            rr = requests.post('http://localhost:5000/lookup/',data=json.dumps(idbatch), headers=headers)
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
    ncommstest()
    ended = datetime.now()
    print ended
    print ended - started
