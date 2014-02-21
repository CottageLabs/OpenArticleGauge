import requests, json
from openarticlegauge import config

es_url = 'http://{host}:9200/oag/log'.format(host=config.DEFAULT_HOST)
es_mapping = {
    "log" : {
        "dynamic_templates" : [
            {
                "default" : {
                    "match" : "*",
                    "match_mapping_type": "string",
                    "mapping" : {
                        "type" : "multi_field",
                        "fields" : {
                            "{name}" : {"type" : "{dynamic_type}", "index" : "analyzed", "store" : "no"},
                            "exact" : {"type" : "{dynamic_type}", "index" : "not_analyzed", "store" : "yes"}
                        }
                    }
                }
            }
        ],
        "properties":{
            "date":{
                "type": "date",
                "index": "not_analyzed",
                "format": "yyyy-MM-dd HH:mm:ss"
            }
        }
    }
}

logfiles = ['1.log','2.log','3.log','4.log','5.log','6.log','7.log']

d = requests.delete(es_url)
c = requests.post(es_url)

p = requests.put(es_url+'/_mapping', data=json.dumps(es_mapping) )

for fl in logfiles:
    f = open(fl,'r')
    count = 0
    for line in f:
        if line.startswith('['):
            rec = {
                'id': fl.replace('.','_')+'_'+str(count),
                'logfile': fl
            }
            count += 1

            #print len(line)
            #print line

            meta, log = line.split('] ',1)

            metaray = meta.strip('[').split(': ')
            rec['date'] = metaray[0].split(',',1)[0]
            rec['type'], rec['process'] = metaray[1].split('/')

            rec['log'] = log.strip()

            #print json.dumps(rec,indent=4)
            r = requests.post(es_url+'/'+rec['id'], data=json.dumps(rec))
            #print r.status_code#, r.json()

    f.close()
                                                                     
