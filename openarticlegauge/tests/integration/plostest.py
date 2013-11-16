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

    # This (or equivalent) is the format that this script is looking for:
    # { "doi" : "10.1371/05-PLME-Q-0128.1" }
    # { "doi" : "10.1371/198d344bc40a75f927c9bc5024279815" }
    # { "doi" : "10.1371/4f6cf3e8df15a" }
    # { "doi" : "10.1371/4f7b4bab0d1a3" }
    # { "doi" : "10.1371/4f7c7cf783354" }
    # { "doi" : "10.1371/4f7f57285b804" }
    # { "doi" : "10.1371/4f7f6dc013d4e" }
    # { "doi" : "10.1371/4f83ebf72317d" }
    # { "doi" : "10.1371/4f84a944d8930" }
    # { "doi" : "10.1371/4f8606b742ef3" }
    # ^ JSON objects, one per line. The objects can include other information as well, e.g.
    # { "doi" : "10.1371/4f8606b742ef3" , "title": "A Title"}
    # is perfectly fine.

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

        # If we are not waiting for each batch of a 1000 to be fully
        # processed before submitting the next one, sleep 10 seconds
        # between requests - it might work without this, just making
        # sure the various OAG server bits have time to do their work.
        # No ID-s should be dropped regardless of this 10s sleep.
        if not wait and count > 0:
            sleep(10)

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
            idbatch = []
            if len(rs['processing']) != 0 and wait:
                # if waiting for confirmation they are all processed, add the processing ones back to the ID list
                # otherwise the empty list sends the loop onto the next batch
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
