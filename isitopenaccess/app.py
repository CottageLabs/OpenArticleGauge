import os
from flask import Flask, render_template, request, make_response

import workflow, config

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

# a display of an embedded facetview pointing to the targeted bibserver instance, and a link to there
@app.route("/search")
def search():
    return render_template('search.html')

# present and accept dispute processing
@app.route("/dispute", methods=['GET','POST'])
@app.route("/dispute/", methods=['GET','POST'])
def dispute():
    return render_template('dispute.html')


@app.route("/lookup", methods=['GET','POST'])
@app.route("/lookup/", methods=['GET','POST'])
@app.route("/lookup/<path:path>", methods=['GET','POST'])
def api_lookup(path=False,ids=[]):
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

    if request.method == 'GET':
        render_template('index.html', results=results)
    else:
        resp = make_response( results )
        resp.mimetype = "application/json"
        return resp




# a potential route for receiving submissions of updates for the index
# decided not to implement at this stage
'''@app.route("/submit", methods=['GET','POST'])
@app.route("/submit/", methods=['GET','POST'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    elif request.method == 'POST':
        # store the received list unless we are going to do some sort of checking on it
        # pass through to bibserver with an API KEY perhaps?
        pass'''


@app.errorhandler(400)
def bad_request(error):
    return render_template('bad_request.html'), 400
    
@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404

    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise whatever is in config.
    port = int(os.environ.get('PORT', config.port))
    app.debug = config.debug
    app.run(host=config.host, port=port)