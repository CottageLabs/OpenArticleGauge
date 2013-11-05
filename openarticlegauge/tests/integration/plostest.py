import requests, json, sys
from time import sleep
import traceback

def plostest():
    wait = False

    if len(sys.argv) > 1:
        if sys.argv[1] == 'wait':
            wait = True
            print 'Going to wait until each ID batch has finished processing before sending in next one.'
            sleep(2)

    # read in the plos list
    # NOTE: the plos list is 78mb so it is not in the repo - pull it manually and place it next to this one
    n = []
    try:
        f = open('plos.json','r')
        for line in f:
            try:
                n.append(json.loads(line))
            except:
                pass
        f.close()
        print len(n)
    except IOError:
        print 'no plos.json found - note it is too long to be in the repo, you need to get a copy manually and put it in this directory'
    ids = []
    for o in n:
        if 'doi' in o:
            ids.append(o['doi'])

    total = len(ids)
    print total

    # send the ID list to the OAG service 1000 at a time
    # loop it until informed they have all been processed
    count = 0
    while len(ids) >= 1000:
        count += 1
        print count
        if len(ids) < 1000:
            idbatch = ids[0:len(ids)-1]
            ids = []
        else:
            idbatch = ids[0:999]
            ids = ids[1000:]
        while len(idbatch):
            headers = {'content-type': 'application/json'}
            try:
                rr = requests.post('http://localhost:5051/lookup/',data=json.dumps(idbatch), headers=headers)
            except Exception:
                print 'Exception while trying to send a batch of ID-s to OAG'
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                print ''.join(line for line in lines)
            try:
                rs = rr.json()
            except ValueError as e:
                print rr.status_code
                print
                print rr.text.encode('utf-8')
            if len(rs['processing']) == 0:
                idbatch = []  # next batch
            else:
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
    plostest()
    ended = datetime.now()
    print ended
    print ended - started
