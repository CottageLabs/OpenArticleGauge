from openarticlegauge import models

print "Adding default handlers"

batch = []
batch_size = 1000
for record in models.Record.iterall():
    licenses = record.data.get("license", [])
    
    trip = False
    for l in licenses:
        prov = l.get("provenance")
        if prov is None:
            l["provenance"] = {}
        handler = prov.get("handler")
        if handler is None:
            trip = True
            prov["handler"] = "oag"
        version = prov.get("handler_version")
        if version is None:
            trip = True
            prov["handler_version"] = "0.0"
            
    if trip:
        batch.append(record.data)
    
    if len(batch) >= batch_size:
        print "writing ", len(batch)
        models.Record.bulk(batch)
        batch = []

if len(batch) > 0:
    print "writing ", len(batch)
    models.Record.bulk(batch)
