import os
from flask import Flask, render_template, request

from flask_negotiate import consumes, produces

import workflow

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


# static pages
@app.route('/')
@produces(HTML)
def hello():
    return render_template('index.html')

# just the api docs here
@app.route("/api")
@produces(HTML)
def api():
    return render_template('api.html')

# just a display of perhaps an embedded facetview pointing to bibsoup.net, and a link to there
@app.route("/search")
@produces(HTML)
def search():
    return render_template('search.html')


@app.route("/submit", methods=['GET','POST'])
@app.route("/submit/", methods=['GET','POST'])
@produces(HTML)
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    elif request.method == 'POST':
        # store the received list unless we are going to do some sort of checking on it
        pass


@app.route("/lookup", methods=['GET','POST'])
@app.route("/lookup/", methods=['GET','POST'])
@app.route("/lookup/<ids>", methods=['GET','POST'])
def api_lookup(ids=[]):
    if request.method == 'GET':
        if ids:
            pass
        # display the static front page with the info
        pass
    else:
        if ids:
            pass # prep the data
        elif request.json:
            pass # prep the data
        else:
            abort(400)
        
        results = workflow.lookup('list of bibjson id objects')
        resp = make_response( results.json() )
        resp.mimetype = "application/json"
        return resp


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
