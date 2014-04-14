"""
Data model objects, some of which extend the DAO for storage purposes

"""

import json, redis, logging
from datetime import datetime

from openarticlegauge import config
from openarticlegauge.dao import DomainObject
from openarticlegauge.core import app
from openarticlegauge.slavedriver import celery

from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

log = logging.getLogger(__name__)

class ModelException(Exception):
    """
    Exception to be thrown when there is a problem constructing or manipulating model objects
    
    """
    def __init__(self, message):
        self.message = message
        super(ModelException, self).__init__(self, message)

class LookupException(Exception):
    """
    Exception to be thrown when there is a problem looking up a record
    
    """
    def __init__(self, message):
        self.message = message
        super(LookupException, self).__init__(self, message)

class BufferException(Exception):
    """
    Exception to be thrown when there is a problem with the storage buffer
    
    """
    def __init__(self, message):
        self.message = message
        super(BufferException, self).__init__(self, message)

class Account(DomainObject, UserMixin):
    __type__ = 'account'

    @classmethod
    def pull_by_email(cls, email):
        res = cls.query(q='email:"' + email + '"')
        if res.get('hits',{}).get('total',0) == 1:
            return cls(**res['hits']['hits'][0]['_source'])
        else:
            return None

    def set_password(self, password):
        self.data['password'] = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.data['password'], password)

    @property
    def email(self):
        return self.data.get("email")

    @property
    def is_super(self):
        #return not self.is_anonymous() and self.id in app.config.get('SUPER_USER', [])
        return False

class Record(DomainObject):
    __type__ = 'record'
    
    @classmethod
    def check_archive(cls, identifier):
        """
        Check the archive layer for an object with the given (canonical) identifier,
        which can be found in the bibjson['identifier']['canonical'] field
        
        arguments:
        identifier -- the identifier of the record to look up.  This should be the canonical identifier of the record
        
        Return a bibjson record or None if none is found
        
        """
        
        result = {}
        if config.BUFFERING:
            # before checking remote, check the buffer queue if one is enabled
            log.debug("checking buffer for " + str(identifier))
            result = cls._check_buffer(identifier)
            if result:
                log.debug(str(identifier) + " found in buffer")
            
        if not result:
            # by just making an ID and GETting and POSTing to it, we can do things faster.
            log.debug("checking remote archive for " + str(identifier))
            _id = identifier.replace('/','_')
            result = cls.pull(_id)
            if result:
                log.debug(str(identifier) + " found in remote archive")
            else:
                log.debug(str(identifier) + " did not yield a result in the archive")

        try:
            return result.data
        except:
            return result

    @classmethod
    def store(cls, bibjson):
        """
        Store the provided bibjson record in the archive (overwriting any item which
        has the same canonical identifier).  Depending on the configuration, this method
        may put the item into a buffer to be written out to storage at some later time
        in the future.
        
        arguments:
        bibjson -- the bibjson record to be stored.  The record must contain a canonical identifier in ['identifier'][n]['canonical']
        
        """
        # normalise the canonical identifier for elastic search
        identifier = None # record this for logging
        for idobj in bibjson.get('identifier',[]):
            if 'canonical' in idobj.keys():
                bibjson['id'] = idobj['canonical'].replace('/','_')
                identifier = idobj['canonical']
        
        if config.BUFFERING:
            log.info("placing item " + identifier + " into the storage buffer")
            
            # just add to the buffer, no need to actually save anything
            cls._add_to_buffer(bibjson)
            return
        else:
            log.info("placing item " + identifier + " directly into storage")
            log.debug("saving bibjson: "+ str(bibjson))
            
            # no buffering, just save this one record
            r = cls(**bibjson)
            r.save()
    
    @classmethod
    def _add_to_buffer(cls, bibjson):
        """
        add the given bibjson record to the storage buffer
        
        arguments:
        bibjson -- the bibjson record to be stored.  The record must contain a canonical identifier in ['identifier'][n]['canonical']
        
        """
        canonical = None
        for identifier in bibjson.get("identifier", []):
            if "canonical" in identifier:
                canonical = identifier['canonical']
                break
        
        if canonical is None:
            raise BufferException("cannot buffer an item without a canonical form of the identifier")
        
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        s = json.dumps(bibjson)
        client.set("id_" + canonical, s)
    
    @classmethod
    def _check_buffer(cls, canonical):
        """
        Check the storage buffer for an item identified by the supplied canonical identifier
        
        arguments:
        identifier -- the identifier of the record to look up.  This should be the canonical identifier of the record
        
        Return a bibjson record or None if none is found
        
        """
        # query the redis cache for the bibjson record and return it
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        record = client.get("id_" + canonical)
        if record is None or record == "":
            return None
        return json.loads(record)
    
    @classmethod
    def flush_buffer(cls, key_timeout=0, block_size=1000):
        """
        Flush the current storage buffer out to the long-term storage (Elasticsearch).  This method
        will return after all of the records have been flushed successfully to storage, and will
        not wait until the key_timeout period has passed (this will happen asynchronously)
        
        keyword arguments:
        key_timeout -- the length of time to live (in seconds) to allocate to each record in the storage buffer.  This is to 
            allow Elasticsearch time to receive and index the records and make them available - while it is
            doing that, the records will remain available in the storage buffer
            
        block_size -- maximum size of the list of records to send to the long-term storage in one HTTP request.
            if there are more records than the block size, multiple HTTP requests will be made, none of which
            will be larger than the block_size.
        
        returns:
        False if there is nothing in the buffer to flush
        True if there are items in the buffer to flush and they are successfully flushed
        
        """
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        
        # get all of the id keys
        ids = client.keys("id_*")
        if len(ids) == 0:
            log.info("storage buffer contains 0 items to be flushed ... returning")
            return False
        log.info("flushing storage buffer of " + str(len(ids)) + " objects")
        
        # retrieve all of the bibjson records associated with those keys
        
        bibjson_records = []
        i = 0
        for identifier in ids:
            # obtain, decode and register the bibjson record to be archived
            s = client.get(identifier)
            obj = json.loads(s)
            bibjson_records.append(obj)
            
            # if we've reached the block size, do a bulk write
            i += 1
            if i >= block_size:
                # bulk load the records
                cls.bulk(bibjson_records)
                
                # reset the registers
                i = 0
                bibjson_records = []
        
        if len(bibjson_records) > 0:
            # bulk load the remaining records
            cls.bulk(bibjson_records)
        
        # set a timeout on the identifiers affected, if desired.  If the key_timeout is 0, this is effectively
        # the same as deleting those keys
        for identifier in ids:
            client.expire(identifier, key_timeout)
        
        return True

class Issue(DomainObject):
    __type__ = 'issue'

class Log(DomainObject):
    __type__ = 'log'

class Error(DomainObject):
    __type__ = "error"

class License(DomainObject):
    __type__ = 'license'

class LicenseStatement(DomainObject):
    __type__ = 'license_statement'

    @property
    def edit_id(self): return self.data['id']

    @property
    def license_statement(self): return self.data.get("license_statement")
    @license_statement.setter
    def license_statement(self, value): self.data['license_statement'] = value

    @property
    def license_type(self): return self.data.get("license_type")
    @license_type.setter
    def license_type(self, value): self.data['license_type'] = value

    @property
    def version(self): return self.data.get("version")
    @version.setter
    def version(self, value): self.data['version'] = value

    @property
    def example_doi(self): return self.data.get("example_doi")
    @example_doi.setter
    def example_doi(self, value): self.data['example_doi'] = value

    @classmethod
    def find_by_statement(cls, statement):
        return cls.q2obj(terms={'license_statement.exact': [statement]}, size=1000000, consistent_order=True)

    def save(self):
        t = self.find_by_statement(self.license_statement)

        if len(t) == 1:
            # just one such statement exists - edit it instead
            print 'editing statement', t[0]['id']
            self.data['id'] = t[0]['id']

        super(LicenseStatement, self).save()

class Publisher(DomainObject):
    __type__ = 'publisher'

    @property
    def journal_urls(self): return self.data.get("journal_urls", [])
    @journal_urls.setter
    def journal_urls(self, data): self.data['journal_urls'] = data

    @property
    def publisher_name(self): return self.data.get("publisher_name", '')
    @publisher_name.setter
    def publisher_name(self, value): self.data['publisher_name'] = value

    @property
    def licenses(self):
        return self.data.get('licenses', [])

    @licenses.setter
    def licenses(self, data): self.data['licenses'] = data

    def add_license(self, lobj):
        lics = self.licenses
        lics.append(lobj)

    def remove_license(self, license_statement):
        lics = self.licenses
        try:
            del lics[license_statement]
        except KeyError:
            pass

    @classmethod
    def all_journal_urls(cls):
        return cls.facets2flatlist(
            facets= { 'journal_urls': { "field": "journal_urls.exact", "size": 10000 } },
            size=0
        )['journal_urls']

    @classmethod
    def find_by_journal_url(cls, url):
        return cls.q2obj(terms={'journal_urls.exact': [url]}, size=1000000, consistent_order=True)


class ResultSet(object):
    """
    Model object to represent the return object from the API.  It represents the following data structure:
    
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
        """
        Construct a new ResultSet object around the list of bibjson_ids supplied to the API
        
        arguments
        bibjson_ids -- list of bibjson identifier objects
        
        """
        self.requested = len(bibjson_ids)
        self.results = []
        self.errors = []
        self.processing = []
        self.bibjson_ids = bibjson_ids
    
    def add_result_record(self, record):
        """
        Add the given record to the result set.  This will inspect the content of the record and
        add it to the appropriate part of the response
        
        arguments
        record -- OAG record object.  See the high level documentation for details on its structure
        
        """
        
        # get the bibjson if it exists
        bibjson = self._get_bibjson(record)
        
        # now find out if it is queued or if the bibjson record is None
        # and use this information to increment the counters
        # if record.get("error") is not None:
        if record.has_error():
            # self.errors.append({"identifier" : record.get('identifier'), "error" : record.error})
            self.errors.append({"identifier" : record.identifier, "error" : record.error})
        # elif record.get('queued', False) or bibjson is None:
        elif record.queued or bibjson is None:
            # self.processing.append({"identifier" : record.get('identifier')})
            self.processing.append({"identifier" : record.identifier })
        else:
            self.results.append(bibjson)
    
    def json(self):
        """
        Get a JSON representation of this object
        
        returns a JSON serialisation of the object
        
        """
        
        obj = {
            "requested" : self.requested,
            "results" :  self.results,
            "errors" :  self.errors,
            "processing" : self.processing
            }
        return json.dumps(obj)
    
    def _get_bibjson(self, record):
        """
        Get the bibjson from the supplied record.  This involves finding the bibjson
        record in record['bibjson'] and reconciling this with any identifiers in record['identifier']
        to ensure that all relevant identifiers are represented.
        
        arguments:
        record -- OAG record object.  See the high level documentation for details on its structure
        
        """
        
        # first get the bibjson record
        # bibjson = record.get('bibjson')
        bibjson = record.bibjson
        
        if bibjson is None:
            return None
        
        # ensure that the identifier is in the bibjson record
        # FIXME: this is pretty blunt, could be a lot smarter, and ultimately unnecessary anyway
        if not bibjson.has_key("identifier"):
            bibjson["identifier"] = []
        found = False
        for identifier in bibjson['identifier']:
            # if identifier.has_key("canonical") and identifier['canonical'] == record['identifier']['canonical']:
            if identifier.has_key("canonical") and identifier['canonical'] == record.canonical:
                found = True
                break
        if not found:
            # bibjson['identifier'].append(record['identifier'])
            bibjson['identifier'].append(record.identifier)
        
        return bibjson

class MessageObject(object):
    """
    {
        "identifier" : {
            "id" : "<raw id provided by the client>",
            "type" : "<type of identifier, e.g doi or pmid>",
            "canonical" : "<canonical form of the identifier>"
        },
        "queued" : True/False,
        "provider" : {
            "url" : ["<provider url, e.g. dereferenced doi>", "..."],
            "doi" : "<provider doi>"
        },
        "bibjson" : {<bibjson object - see http://bibjson.org>},
        "error" : "<any error message>",
        "licensed" : True/False
    }
    
    "licensed" allows us to tell in the back end if the record had a licence
    attached to it prior to being stripped down to be sent into the back-end.
    
    """
    def __init__(self, bid=None, record=None, bibjson=None):
        """
        Create a new Message object using combinations of the provided arguments.
        
        bid alone creates a new record with that identifier
        record alone seeds this object with a full record object
        bibjson alone seeds this object with a record containing that bibjson
        record + bibjson seeds this object with the provided record, but its bibjson is overwritten
        
        arguments
        bid -- bibjson identifier object or just an id string
        record -- full internal representation of the message object
        bibjson -- bibjson record
        
        """
        self.record = None
        if bid:
            if isinstance(bid, dict):
                if "id" not in bid:
                    raise ModelException("MessageObject must be constructed with an id, or a valid bibjson identifier")
            else:
                bid = {"id" : bid}
            self.record = { "identifier" : bid }
        if record:
            self.record = record
        if bibjson:
            if self.record is None:
                self.record = {}
            self.record["bibjson"] = bibjson
        if self.record is None:
            self.record = {}
    
    ###############################################
    ## Representation functions
    ###############################################
    
    def json(self, **kwargs):
        return json.dumps(self.record, **kwargs)
    
    def __str__(self):
        return str(self.record)
    
    ###############################################
    ## Operational functions
    ###############################################
    
    def merge(self, bibjson):
        ls = bibjson.get("license", [])
        for l in ls:
            self.add_license_object(l)
    
    def prep_for_backend(self):
        self.set_licensed_flag()
        self.remove_bibjson()
        return self.record
    
    def add_identifier_to_bibjson(self):
        """
        Take the supplied bibjson identifier object and ensure that it has been added
        to the supplied bibjson object.  The bibjson object may already contain the
        identifier object, in which case this method will not make any changes.
        """
        
        """
        # FIXME: this is pretty blunt, could be a lot smarter
        if not bibjson.has_key("identifier"):
            bibjson["identifier"] = []
        found = False
        for identifier in bibjson['identifier']:
            if identifier.has_key("canonical") and identifier['canonical'] == bibjson['identifier']['canonical']:
                found = True
                break
        if not found:
            bibjson['identifier'].append(identifier)
        """
        
        # prep the bibjson record to receive an identifier
        if "bibjson" not in self.record:
            self.record["bibjson"] = {}
        if "identifier" not in self.record["bibjson"]:
            self.record["bibjson"]["identifier"] = []
        
        incoming = self.record.get("identifier", {}).get("canonical")
        existing = [ident.get("canonical") for ident in self.record.get("bibjson", {}).get("identifier", []) if ident.get("canonical") is not None]
        
        if incoming is None:
            raise ModelException("can't add identifier to bibjson unless it has a canonical form")
        
        if incoming not in existing:
            self.record["bibjson"]["identifier"].append(self.record.get("identifier"))
    
    ###############################################
    ## Various simple property getter/setters
    ###############################################
    
    # identifier stuff
    
    @property
    def identifier(self):
        return self.record.get("identifier")
    
    @property
    def id(self):
        return self.record.get("identifier", {}).get("id")
    
    @id.setter
    def id(self, val):
        if "identifier" not in self.record:
            self.record["identifier"] = {}
        self.record["identifier"]["id"] = val
    
    def has_id(self):
        return "id" in self.record.get("identifier", {})
    
    @property
    def identifier_type(self):
        return self.record.get("identifier", {}).get("type")
    
    @identifier_type.setter
    def identifier_type(self, type):
        if "identifier" not in self.record:
            self.record["identifier"] = {}
        self.record["identifier"]["type"] = type
    
    def has_type(self):
        return "type" in self.record.get("identifier", {})
    
    @property
    def canonical(self):
        return self.record.get("identifier", {}).get("canonical")
    
    @canonical.setter
    def canonical(self, canonical):
        if "identifier" not in self.record:
            self.record["identifier"] = {}
        self.record["identifier"]["canonical"] = canonical
    
    # queue
    
    @property
    def queued(self):
        return self.record.get("queued", False)
    
    @queued.setter
    def queued(self, val):
        self.record["queued"] = val
        
    # provider
    
    @property
    def provider(self):
        return self.record.get("provider")
    
    def has_provider(self):
        return "provider" in self.record
    
    @property
    def provider_doi(self):
        return self.record.get("provider", {}).get("doi")

    @property
    def doi_without_prefix(self):
        doi = self.provider_doi

        # is it a string? could get None too
        # convention dictates to test for capability, not identity though
        if getattr(doi, 'startswith', None):
            # if it can be lowercased, then do it - higher chance of matching the prefix
            if getattr(doi, 'lower', None):
                if doi.lower().startswith('doi:'):
                    return doi[4:]
            # we can use startswith, but can't lowercase it (?!) - just check for the prefix
            if doi.startswith('doi:') or doi.startswith('DOI:'):
                    return doi[4:]
        return doi
    
    @property
    def provider_urls(self):
        return self.record.get("provider", {}).get("url", [])
    
    def add_provider_url(self, url):
        """
        Record a provider url in the record
        
        arguments:
        url -- the url to be added to the provider record
        
        """
        if not "provider" in self.record:
            self.record['provider'] = {}
        if not "url" in self.record["provider"]:
            self.record["provider"]["url"] = []
        if url not in self.record['provider']['url']:
            self.record['provider']['url'].append(url)
        
    def add_provider_urls(self, urls):
        """
        Record a list of provider urls in the record
        
        arguments:
        urls -- the urls to be added to the provider record
        
        """
        for url in urls:
            self.add_provider_url(url)
    
    def set_provider_doi(self, doi):
        """
        Record a DOI in the provider part of the record
        
        arguments:
        doi -- the doi to be added to the provider record
        """
        if not "provider" in self.record:
            self.record['provider'] = {}
        self.record["provider"]["doi"] = doi
    
    # bibjson
    
    @property
    def bibjson(self):
        return self.record.get("bibjson")
    
    @bibjson.setter
    def bibjson(self, bj):
        self.record["bibjson"] = bj
    
    def has_bibjson(self):
        return "bibjson" in self.record
    
    def remove_bibjson(self):
        if "bibjson" in self.record:
            del self.record["bibjson"]
    
    # error
    
    @property
    def error(self):
        return self.record.get("error")
    
    @error.setter
    def error(self, val):
        self.record["error"] = val
    
    def has_error(self):
        return "error" in self.record
    
    # licensed flag
    
    def set_licensed_flag(self):
        self.record["licensed"] = len(self.record.get("bibjson", {}).get("license", [])) > 0
    
    def was_licensed(self):
        return self.record.get("licensed", False)
    
    # license specifically
    
    @property
    def license(self):
        return self.record.get("bibjson", {}).get("license", [])
    
    def has_license(self):
        return "license" in self.record.get("bibjson", {}) and len(self.record.get("bibjson", {}).get("license", [])) > 0
    
    def add_license_object(self, license):
        if "bibjson" not in self.record:
            self.record["bibjson"] = {}
        if "license" not in self.record['bibjson']:
            self.record['bibjson']['license'] = []
        
        self.record['bibjson']['license'].append(license)
    
    def add_license(self, 
                    description="",
                    title="",
                    url="",
                    version="",
                    jurisdiction="",
                    type="",
                    open_access=False,
                    BY="",
                    NC="",
                    ND="",
                    SA="",
                    error_message="",
                    suggested_solution="",
                    category="",
                    provenance_description="",
                    agent=config.agent,
                    source="",
                    source_size=-1,
                    date=datetime.strftime(datetime.now(), config.date_format),
                    handler="",
                    handler_version=""):
        """
        Add a licence with the supplied keyword parameters to the record in the appropriate format.
        
        The format of the licence is as follows:
        {
            "description": "",
            "title": "",
            "url": licence_url,
            "version": "",
            "jurisdiction": "",
            "type": "failed-to-obtain-license",
            "open_access": False,
            "BY": "",
            "NC": "",
            "ND": "",
            "SA": "",
            "error_message": why,
            "suggested_solution": suggested_solution,
            "provenance": {
                "category": "page_scrape",
                "description": self.gen_provenance_description_fail(source_url),
                "agent": config.agent,
                "source": source_url,
                "source_size" : source_size,
                "date": datetime.strftime(datetime.now(), config.date_format),
                "handler" : self._short_name,
                "handler_version" : self.__version__
            }
        }
        
        keyword_arguments:
        see the top level documentation for details on the meaning of each field - they map consistently to the parts
        of the licence record
        
        """
        
        if "bibjson" not in self.record:
            self.record["bibjson"] = {}
        if "license" not in self.record['bibjson']:
            self.record['bibjson']['license'] = []
        
        self.record['bibjson']['license'].append(
            {
                "description": description,
                "title": title,
                "url": url,
                "version": version,
                "jurisdiction": jurisdiction,
                "type": type,
                "open_access": open_access,
                "BY": BY,
                "NC": NC,
                "ND": ND,
                "SA": SA,
                "error_message": error_message,
                "suggested_solution": suggested_solution,
                "provenance": {
                    "category": category,
                    "description": provenance_description,
                    "agent": agent,
                    "source": source,
                    "source_size" : source_size,
                    "date": date,
                    "handler" : handler,
                    "handler_version" : handler_version
                }
            }
        )
    
@celery.task(name="openarticlegauge.models.flush_buffer")
def flush_buffer():
    """
    Celery task for flushing the storage buffer.  This should be promoted onto a
    processing queue by Celery Beat (see the celeryconfig).  This will process will
    lock the buffer so that parallel execution is not possible.
    
    returns
    False if no buffering is necessary (configuration) or possible (locked)
    True if buffering has been handled
    
    """
    
    # if we are not buffering, don't do anything
    if not config.BUFFERING:
        log.info("BUFFERING = False ; flush_buffer is superfluous, aborting")
        return False
    
    # check to see if we are already running a buffering process    
    client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
    lock = client.get("flush_buffer_lock")
    if lock is not None:
        log.warn("flush_buffer ran before previous iteration had completed - consider increasing the gaps between the run times for this scheduled task")
        return False
    
    # if we are not already running the buffering process, then carry on...
    
    # set a lock on this process, so that it doesn't run twice at the same time (see checks above)
    client.set("flush_buffer_lock", "lock")
    
    # call flush on the record objects that are buffered
    Record.flush_buffer(key_timeout=config.BUFFER_GRACE_PERIOD, block_size=config.BUFFER_BLOCK_SIZE)
    
    # set an expiry time on the lock, which is consistent with the expiry time applied to the 
    # buffered items.  This means this method will only run again once all the previously buffered
    # items have been removed from the buffer zone.
    client.expire("flush_buffer_lock", config.BUFFER_GRACE_PERIOD)
    
    # return true to indicate that the function ran
    return True
