'''
An elasticsearch query pass-through.
Has auth control, so it is better than exposing your ES index directly.
'''

import json, urllib2

from flask import Blueprint, request, abort, make_response

import isitopenaccess.models as models
from isitopenaccess.core import app
import isitopenaccess.util as util


blueprint = Blueprint('query', __name__)


# pass queries direct to index. POST only for receipt of complex query objects
@blueprint.route('/<path:path>', methods=['GET','POST'])
@blueprint.route('/', methods=['GET','POST'])
@util.jsonp
def query(path='Record'):
    pathparts = path.strip('/').split('/')
    subpath = pathparts[0]
    if subpath.lower() in app.config['NO_QUERY_VIA_API']:
        abort(401)
    klass = getattr(models, subpath[0].capitalize() + subpath[1:] )
    
    if len(pathparts) > 1 and pathparts[1] == '_mapping':
        resp = make_response( json.dumps(klass().query(endpoint='_mapping')) )
    elif len(pathparts) == 2 and pathparts[1] not in ['_mapping','_search']:
        if request.method == 'POST':
            abort(401)
        else:
            rec = klass().pull(pathparts[1])
            if rec:
                if ( not app.config['ANONYMOUS_SEARCH_FILTER'] ) or ( app.config['ANONYMOUS_SEARCH_FILTER'] and rec['visible'] and rec['accessible'] ):
                    resp = make_response( rec.json )
                else:
                    abort(401)
            else:
                abort(404)
    else:
        if request.method == "POST":
            if request.json:
                qs = request.json
            else:
                qs = dict(request.form).keys()[-1]
        elif 'q' in request.values:
            qs = {'query': {'query_string': { 'query': request.values['q'] }}}
        elif 'source' in request.values:
            qs = json.loads(urllib2.unquote(request.values['source']))
        else: 
            qs = ''
        for item in request.values:
            if item not in ['q','source','callback','_'] and isinstance(qs,dict):
                qs[item] = request.values[item]
        if 'sort' not in qs and app.config['SEARCH_SORT']:
            qs['sort'] = {app.config['SEARCH_SORT'].rstrip(app.config['FACET_FIELD']) + app.config['FACET_FIELD'] : {"order":app.config.get('SEARCH_SORT_ORDER','asc')}}
        #if app.config['ANONYMOUS_SEARCH_FILTER'] and current_user.is_anonymous():
        #    terms = {'visible':True,'accessible':True}
        #else:
        terms = ''
        resp = make_response( json.dumps(klass().query(q=qs, terms=terms)) )
    resp.mimetype = "application/json"
    return resp

