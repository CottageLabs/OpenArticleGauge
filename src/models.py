class ResultSet(object):
    """
    {
	    "requested": number_requested_in_batch,
	    "available": number_of_those_already_known,
	    "processing": number_waiting_for_processing,
	    "results": [
		    the list of bibjson record objects already known
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
