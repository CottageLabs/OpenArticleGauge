import os
from flask import Flask, render_template, request

from flask_negotiate import consumes, produces

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print "You need to have a json lib installed"
        import sys
        sys.exit(1)

HTML = "text/html"
JSON = "application/json"

app = Flask(__name__)

# Put a 3M limit on uploads
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 3

@app.route('/')
@produces(HTML)
def hello():
    return render_template('index.html')

@app.route("/lookup/<ids>", methods=['GET'])
@produces(HTML)
def get_lookup(ids):
    # Unpleasant URL form here for multiples?
    return "\n".join(ids.split(","))

@app.route("/lookup/<ids>", methods=['GET'])
@produces(JSON)
def get_lookup_json(ids):
    return "\n".join(ids.split(","))

@app.route("/lookup/", methods=['POST'])
@produces(HTML)
def lookup():
    # Expects 'query' and (optionally) 'format' and 'ignore_unknown_ids'
    # ('format' used to force content negotiation)
    # If param 'query' is not in the form, lookup will return a 
    # HTTP 400 Bad Request so this is fine:
    ids = request.form['query']
    
    # parse ID(s) from input
    # pass ID(s) to background task to lookup unknown ones
    #
    #   if HTML requested:
    #     redirect user to /id/<ID>
    #       or
    #     construct page that uses JS to pull in info for each ID queried async.
    return "Got something: '%s'" % ids

@app.route("/lookup/", methods=['POST'])
@consumes(JSON)
@produces(JSON)
def api_lookup():
    #   if JSON:
    #     if ignore_unknown_ids in request is 'True'
    #       find and return cached/stored results for IDs that are known
    #     else:
    #       FIXME: Not sure. Should the connection persist til all IDs are
    #       attempted?
    
    # Check content-length and reject if above an arbitrary value for RAM sanity
    # -> accept up to 3MB of transmitted data - set on line 22 above.
    try:
        passed_json = json.loads(request.data)
        return '{"response": "Got parsable JSON"}'
    except ValueError:
        abort(400)

@app.errorhandler(400)
def bad_request(error):
    return render_template('bad_request.html'), 400
    
@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
