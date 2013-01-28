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
        self.available = 0
        self.processing = 0
        self.errors = 0
        self.results = []
        self.bibjson_ids = bibjson_ids
    
    def add_result_record(self, record):
        # first get the bibjson record
        bibjson = record.get('bibjson')
        
        # now find out if it is queued or if the bibjson record is None
        # and use this information to increment the counters
        if record.get("error") is not None:
            self.errors += 1
            self.results.append({"identifier" : record.get('identifier'), "error" : record.get("error")})
        if record.get('queued', False) or bibjson is None:
            self.processing += 1
            self.results.append({"identifier" : record.get('identifier')})
        else:
            self.available += 1
            self.results.append(record.get("bibjson"))
        

class LookupException(Exception):
    def __init__(self, value):
        super(LookupException, self).__init__(self, value)
