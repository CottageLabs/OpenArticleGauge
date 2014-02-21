"""
Generic Data Access Object for mediating between the OAG application and the
storage back end.

This implementation provides storage in an Elasticsearch index.

"""

import os, json, requests, uuid, logging
from datetime import datetime
from copy import deepcopy

from openarticlegauge.core import app #, current_user

class DomainObject(dict):
    """
    All models in models.py should inherit this DomainObject to know how to save themselves in the index and so on.
    You can overwrite and add to the DomainObject functions as required. See models.py for some examples.
    
    """

    __type__ = None # set the type on the model that inherits this

    def __init__(self, **kwargs):
        super(DomainObject, self).__init__(**kwargs)
        if '_source' in kwargs:
            self.data = dict(kwargs['_source'])
            self.meta = dict(kwargs)
            del self.meta['_source']
        else:
            self.data = dict(kwargs)
            
    @classmethod
    def target(cls):
        t = app.config['ELASTIC_SEARCH_HOST'].rstrip('/') + '/'
        t += app.config['ELASTIC_SEARCH_DB'] + '/' + cls.__type__ + '/'
        return t
    
    @classmethod
    def makeid(cls):
        '''Create a new id for data object
        overwrite this in specific model types if required'''
        return uuid.uuid4().hex

    @property
    def id(self):
        return self.data.get('id', None)
        
    @property
    def version(self):
        return self.meta.get('_version', None)

    @property
    def json(self):
        return json.dumps(self.data)

    def save(self):
        if 'id' in self.data:
            id_ = self.data['id'].strip()
        else:
            id_ = self.makeid()
            self.data['id'] = id_
        
        self.data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H%M")

        if 'created_date' not in self.data:
            self.data['created_date'] = datetime.now().strftime("%Y-%m-%d %H%M")
            
        if 'author' not in self.data:
            try:
                self.data['author'] = current_user.id
            except:
                self.data['author'] = "anonymous"

        r = requests.post(self.target() + self.data['id'], data=json.dumps(self.data))


    @classmethod
    def bulk(cls, bibjson_list, refresh=False):
        data = ''
        for r in bibjson_list:
            data += json.dumps( {'index':{'_id':r['id']}} ) + '\n'
            data += json.dumps( r ) + '\n'
        r = requests.post(cls.target() + '_bulk', data=data)
        if refresh:
            cls.refresh()
        return r.json()


    @classmethod
    def refresh(cls):
        r = requests.post(cls.target() + '_refresh')
        return r.json()


    @classmethod
    def pull(cls, id_):
        '''Retrieve object by id.'''
        if id_ is None:
            return None
        try:
            out = requests.get(cls.target() + id_)
            if out.status_code == 404:
                return None
            else:
                return cls(**out.json())
        except:
            return None

    @classmethod
    def all(cls):
        res = cls.query(q='*')
        if res['hits']['total'] <= 0:
            return []

        hits = res['hits']['hits']
        results = [cls(**h) for h in hits]
        return results

    @classmethod
    def q2obj(cls, **kwargs):
        res = cls.query(**kwargs)
        if res['hits']['total'] <= 0:
            return []

        hits = res['hits']['hits']
        results = [cls(**h['_source']) for h in hits]
        return results

    @classmethod
    def query(cls, recid='', endpoint='_search', q='', terms=None, facets=None, **kwargs):
        '''Perform a query on backend.

        :param recid: needed if endpoint is about a record, e.g. mlt
        :param endpoint: default is _search, but could be _mapping, _mlt, _flt etc.
        :param q: maps to query_string parameter if string, or query dict if dict.
        :param terms: dictionary of terms to filter on. values should be lists. 
        :param facets: dict of facets to return from the query.
        :param kwargs: any keyword args as per
            http://www.elasticsearch.org/guide/reference/api/search/uri-request.html
        '''
        if recid and not recid.endswith('/'): recid += '/'
        if isinstance(q,dict):
            query = q
        elif q:
            query = {'query': {'query_string': { 'query': q }}}
        else:
            query = {'query': {'match_all': {}}}

        if facets:
            if 'facets' not in query:
                query['facets'] = {}
            for k, v in facets.items():
                query['facets'][k] = {"terms":v}

        if terms:
            boolean = {'must': [] }
            for term in terms:
                if not isinstance(terms[term],list): terms[term] = [terms[term]]
                for val in terms[term]:
                    obj = {'term': {}}
                    obj['term'][ term ] = val
                    boolean['must'].append(obj)
            if q and not isinstance(q,dict):
                boolean['must'].append( {'query_string': { 'query': q } } )
            elif q and 'query' in q:
                boolean['must'].append( query['query'] )
            query['query'] = {'bool': boolean}

        for k,v in kwargs.items():
            if k == '_from':
                query['from'] = v
            else:
                query[k] = v

        if endpoint in ['_mapping']:
            r = requests.get(cls.target() + recid + endpoint)
        else:
            r = requests.post(cls.target() + recid + endpoint, data=json.dumps(query))
        return r.json()

    def accessed(self):
        if 'last_access' not in self.data:
            self.data['last_access'] = []
        try:
            usr = current_user.id
        except:
            usr = "anonymous"
        self.data['last_access'].insert(0, { 'user':usr, 'date':datetime.now().strftime("%Y-%m-%d %H%M") } )
        r = requests.put(self.target() + self.data['id'], data=json.dumps(self.data))

    def delete(self):        
        r = requests.delete(self.target() + self.id)
    
    @classmethod
    def iterate(cls, q, page_size=1000, limit=None):
        q["size"] = page_size
        q["from"] = 0
        counter = 0
        while True:
            # apply the limit
            if limit is not None and counter >= limit:
                break
            
            res = cls.query(q=q)
            rs = [r.get("_source") for r in res.get("hits", {}).get("hits", [])]
            # print counter, len(rs), res.get("hits", {}).get("total"), len(res.get("hits", {}).get("hits", [])), json.dumps(q)
            if len(rs) == 0:
                break
            for r in rs:
                # apply the limit (again)
                if limit is not None and counter >= limit:
                    break
                counter += 1
                yield cls(**r)
            q["from"] += page_size   
    
    @classmethod
    def iterall(cls, page_size=1000, limit=None):
        return cls.iterate(deepcopy(all_query), page_size, limit)

########################################################################
## Some useful ES queries
########################################################################

all_query = { 
    "query" : { 
        "match_all" : { }
    }
}
