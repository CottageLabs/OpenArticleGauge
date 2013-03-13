import json

from isitopenaccess.dao import DomainObject

from isitopenaccess.core import app

class Record(DomainObject):
    __type__ = 'record'
    
    @classmethod
    def check_archive(cls, identifier):
        """
        Check the archive layer for an object with the given (canonical) identifier,
        which can be found in the bibjson['identifier']['canonical'] field
        
        Return a bibjson record
        """
        
        result = {}
        if app.config['BUFFERING']:
            # before checking remote, check the redis buffer queue if one is enabled
            result = {} # should update result to the matching record object found on buffer queue if any
            
        if not result:
            # by just making an ID and GETting and POSTing to it, we can do things faster.
            _id = identifier.replace('/','_')
            result = cls.pull(_id)

        try:
            return result.data
        except:
            return result

    @classmethod
    def store(cls, bibjson):
        """
        Store the provided bibjson record in the archive (overwriting any item which
        has the same canonical identifier)
        """
        
        for idobj in bibjson.get('identifier',[]):
            if 'canonical' in idobj.keys():
                bibjson['id'] = idobj['canonical'].replace('/','_')
        
        if app.config['BUFFERING']:
            # append this bibjson record to the buffer somehow
            buf = 'whatever it was plus this new record'
            # if buffer size limit reached or buffer timeout reached
            if False: # change this to proper decision
                cls.bulk('list of the records in the buffer')
                # flush the buffer however that is done
        else:
            # no buffering, just save this one record
            r = cls(**bibjson)
            r.save()


class Dispute(DomainObject):
    __type__ = 'dispute'


class Log(DomainObject):
    __type__ = 'log'


class ResultSet(object):
    """
    {
	    "requested" : number_requested_in_batch,
	    "results" : [
		    the list of bibjson record objects already known
	    ],
	    "errors" : [
		    a list of JSON objects with an "identifier" key and an "error" key
	    ],
	    "processing" : [
		    a list of bibjson identifier objects that are on the queue
	    ]
    }
    """
    def __init__(self, bibjson_ids=[]):
        # FIXME: this is probably not the right way to initialise the object, or store
        # the internal state, but we can fix that later.  Important, first, just to make it work
        self.requested = len(bibjson_ids)
        self.results = []
        self.errors = []
        self.processing = []
        self.bibjson_ids = bibjson_ids
    
    def add_result_record(self, record):
        # get the bibjson if it exists
        bibjson = self._get_bibjson(record)
        
        # now find out if it is queued or if the bibjson record is None
        # and use this information to increment the counters
        if record.get("error") is not None:
            self.errors.append({"identifier" : record.get('identifier'), "error" : record.get("error")})
        elif record.get('queued', False) or bibjson is None:
            self.processing.append({"identifier" : record.get('identifier')})
        else:
            self.results.append(bibjson)
    
    def json(self):
        obj = {
            "requested" : self.requested,
            "results" :  self.results,
            "errors" :  self.errors,
            "processing" : self.processing
            }
        return json.dumps(obj)
    
    def _get_bibjson(self, record):
        # first get the bibjson record
        bibjson = record.get('bibjson')
        
        if bibjson is None:
            return None
        
        # ensure that the identifier is in the bibjson record
        # FIXME: this is pretty blunt, could be a lot smarter, and ultimately unnecessary anyway
        if not bibjson.has_key("identifier"):
            bibjson["identifier"] = []
        found = False
        for identifier in bibjson['identifier']:
            if identifier.has_key("canonical") and identifier['canonical'] == record['identifier']['canonical']:
                found = True
                break
        if not found:
            bibjson['identifier'].append(record['identifier'])
        
        return bibjson

class LookupException(Exception):
    def __init__(self, message):
        self.message = message
        super(LookupException, self).__init__(self, message)
