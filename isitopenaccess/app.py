import os, json, urllib2
from flask import Flask, render_template, request, make_response
from functools import wraps

import workflow, config, archive, dispute

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print "You need to have a json lib installed"
        import sys
        sys.exit(1)


app = Flask(__name__)

# Put a limit on uploads
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 3


# ensures query endpoint will handle JSONP
def jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            return app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function

def _request_wants_json():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']:
        best = True
    else:
        best = False
    if request.values.get('format','').lower() == 'json' or request.path.endswith(".json"):
        best = True
    return best


# a query endpoint so we can expose what is in the index without leaving it open to attack
# pass queries direct to index. POST only for receipt of complex query objects
@app.route('/query/<tid>')
@app.route('/query', methods=['GET','POST'])
@app.route('/query/', methods=['GET','POST'])
@jsonp
def query(tid=False):    
    if tid:
        rec = archive.retrieve(tid)
        if rec:
            resp = make_response( json.dumps(rec) )
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
            qs = {'query': {'match_all': {}}}
        for item in request.values:
            if item not in ['q','source','callback','_']:
                qs[item] = request.values[item]
        resp = make_response( json.dumps(archive.query(q=qs)) )
    resp.mimetype = "application/json"
    return resp


# static front page
@app.route('/')
def hello():
    return render_template('index.html')

# about page with a bit more info
@app.route('/about')
def about():
    return render_template('about.html')

# about page with a bit more info
@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    elif request.method == 'POST':
        pass

# the info for devs goes here
@app.route("/developers")
def dev():
    return render_template('developers/index.html')

# the info about the api goes here
@app.route("/developers/api")
def api():
    return render_template('developers/api.html')

# a display of an embedded facetview for browsing the stored records
@app.route("/developers/search")
def search():
    return render_template('developers/search.html')

# dev explanation of how to write a plugin
@app.route("/developers/plugins")
def plugins():
    return render_template('developers/plugins.html')

# present and accept dispute processing
@app.route("/dispute", methods=['GET','POST'])
@app.route("/dispute.json", methods=['GET','POST'])
@app.route("/dispute/", methods=['GET','POST'])
@app.route("/dispute/<path:path>", methods=['GET','POST'])
@jsonp
def dispute(path=''):
    givejson = _request_wants_json()
    path = path.replace('.json','')

    d = {}
    
    if path:
        d = dispute.retrieve(path)

    if request.method == 'GET':
        return render_template('dispute.html', dispute=d)
    elif request.method == 'POST':
        if not d and request.json:
            d = dispute.new(**request.json)
        else:
            # add to the dispute and save
            pass
        # should email someone here too perhaps
        if config.contact_email:
            pass
        resp = make_response( results )
        resp.mimetype = "application/json"
        return resp
    else:
        abort(404)


@app.route("/lookup", methods=['GET','POST'])
@app.route("/lookup.json", methods=['GET','POST'])
@app.route("/lookup/", methods=['GET','POST'])
@app.route("/lookup/<path:path>", methods=['GET','POST'])
@jsonp
def api_lookup(path='',ids=[]):
    givejson = _request_wants_json()
    path = path.replace('.json','')

    idlist = []
    if ids and isinstance(ids,basestring):
        idlist = [ {"id":i} for i in ids.split(',') ]
    elif ids:
        for i in ids:
            if isinstance(i,basestring):
                idlist.append({"id":i})
            else:
                idlist.append(i)
    elif request.json:
        for item in request.json:
            if isinstance(item,dict):
                idlist.append(item)
            else:
                idlist.append({"id":item})
    elif path and len(path) > 0:
        idlist = [ {"id":i} for i in path.split(',') ]

    if idlist:
        results = workflow.lookup(idlist).json()
    else:
        results = json.dumps({})

    if request.method == 'GET' and not givejson:
        if path:
            triggered = idlist
        else:
            triggered = False
        return render_template('index.html', results=results, triggered=triggered)
    else:
        resp = make_response( results )
        resp.mimetype = "application/json"
        return resp



@app.errorhandler(400)
def bad_request(error):
    return render_template('bad_request.html'), 400
    
@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404

    
if __name__ == '__main__':
    # wipe the redis temp cache (not the non-temp one)
    import redis
    client = redis.StrictRedis(host=config.redis_cache_host, port=config.redis_cache_port, db=config.redis_cache_db)
    client.flushdb()

    # Bind to PORT if defined, otherwise whatever is in config.
    port = int(os.environ.get('PORT', config.port))
    app.debug = config.debug
    app.run(host=config.host, port=port)
