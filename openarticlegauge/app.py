import os, json, urllib2
from flask import Flask, render_template, request, make_response
from functools import wraps

from openarticlegauge.view.contact import blueprint as contact
from openarticlegauge.view.query import blueprint as query
from openarticlegauge.view.issue import blueprint as issue
from openarticlegauge.view.lookup import blueprint as lookup

from openarticlegauge.core import app

app.register_blueprint(contact, url_prefix='/contact')
app.register_blueprint(query, url_prefix='/query')
app.register_blueprint(issue, url_prefix='/issue')
app.register_blueprint(lookup, url_prefix='/lookup')


# static front page
@app.route('/')
def hello():
    return render_template('index.html')


# about page with a bit more info
@app.route('/about')
def about():
    return render_template('about.html')


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


@app.errorhandler(400)
def bad_request(error):
    return render_template('bad_request.html'), 400
    
@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404

    
if __name__ == '__main__':

    # Bind to PORT if defined, otherwise whatever is in config.
    port = int(os.environ.get('PORT', app.config['PORT']))
    app.debug = app.config['DEBUG']
    app.run(host=app.config['HOST'], port=port)
