import os, json, urllib2
from flask import Flask, render_template, request, make_response
from functools import wraps
from flask.ext.login import login_user, current_user
from openarticlegauge.core import app, login_manager
from openarticlegauge import models

from openarticlegauge.view.contact import blueprint as contact
from openarticlegauge.view.query import blueprint as query
from openarticlegauge.view.issue import blueprint as issue
from openarticlegauge.view.lookup import blueprint as lookup
from openarticlegauge.view.account import blueprint as account
from openarticlegauge.view.admin import blueprint as admin
from openarticlegauge.view.license_form import blueprint as license_form
from openarticlegauge.view.resolve_doi import blueprint as resolve_doi

app.register_blueprint(contact, url_prefix='/contact')
app.register_blueprint(license_form, url_prefix='/license_statement')
app.register_blueprint(query, url_prefix='/query')
app.register_blueprint(issue, url_prefix='/issue')
app.register_blueprint(account, url_prefix="/account")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(resolve_doi, url_prefix='/resolve_doi')

# breaks the blueprint abstraction but needed to allow /lookup route
# without trailing slash
from openarticlegauge.view.lookup import api_lookup

# allow POST-ing to /lookup without the trailing slash
# this definition has to come before the lookup blueprint is registered
@app.route('/lookup', methods=['POST'])
def lookup_without_trailing_slash():
    return api_lookup()

app.register_blueprint(lookup, url_prefix='/lookup')

############################################################
## Auth stuff
############################################################

@login_manager.user_loader
def load_account_for_login_manager(userid):
    out = models.Account.pull(userid)
    return out

@app.context_processor
def set_current_context():
    """ Set some template context globals. """
    return dict(current_user=current_user, app=app)

'''
@app.before_request
def standard_authentication():
    """Check remote_user on a per-request basis."""
    remote_user = request.headers.get('REMOTE_USER', '')
    if remote_user:
        user = models.Account.pull(remote_user)
        if user:
            login_user(user, remember=False)
    # add a check for provision of api key
    elif 'api_key' in request.values:
        res = models.Account.query(q='api_key:"' + request.values['api_key'] + '"')['hits']['hits']
        if len(res) == 1:
            user = models.Account.pull(res[0]['_source']['id'])
            if user:
                login_user(user, remember=False)
'''

##############################################################

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

# dev explanation of the backend
@app.route("/developers/backend")
def backend():
    return render_template('developers/backend.html')


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
