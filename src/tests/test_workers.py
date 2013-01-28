from workflow import start_back_end
import time
record = {"id" : "123456", "type" : "doi", "canonical" : "doi:123456", "queued": True}
res = start_back_end(record)
while not res.ready():
    time.sleep(1)
print res.result
