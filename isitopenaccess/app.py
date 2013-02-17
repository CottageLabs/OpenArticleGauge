import os
from flask import Flask, render_template, request

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


app = Flask(__name__)

# Put a limit on uploads
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 3


# static front page
@app.route('/')
def hello():
    return render_template('index.html')

# the api docs here
@app.route("/api")
def api():
    return render_template('api.html')

# a display of an embedded facetview pointing to bibsoup.net, and a link to there
@app.route("/search")
def search():
    return render_template('search.html')


@app.route("/lookup", methods=['GET','POST'])
@app.route("/lookup/", methods=['GET','POST'])
@app.route("/lookup/<ids>", methods=['GET','POST'])
def api_lookup(ids=[]):
    idlist = []
    if ids:
        idlist = [ {"id":i} for i in ids.split(',') ]
    elif request.json:
        idlist = request.json

    if idlist:
        results = workflow.lookup(idlist).json()
    else:
        results = json.dumps({})

    if request.method == 'GET':
        render_template('index.html', results=results)
    else:
        resp = make_response( results )
        resp.mimetype = "application/json"
        return resp


@app.route("/submit", methods=['GET','POST'])
@app.route("/submit/", methods=['GET','POST'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    elif request.method == 'POST':
        # store the received list unless we are going to do some sort of checking on it
        # pass through to bibserver with an API KEY perhaps?
        pass


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
