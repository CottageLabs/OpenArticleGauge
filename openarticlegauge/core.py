import os, requests, json, redis
from flask import Flask

from openarticlegauge import config, licenses
from flask.ext.login import LoginManager, current_user
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    configure_app(app)
    if app.config['INITIALISE_INDEX']: initialise_index(app)
    prep_redis(app)
    setup_error_email(app)
    login_manager.setup_app(app)
    return app

def configure_app(app):
    app.config.from_object(config)
    # parent directory
    here = os.path.dirname(os.path.abspath( __file__ ))
    config_path = os.path.join(os.path.dirname(here), '..', 'app.cfg')  # this file will be in the package dir, app.cfg is at the root of the repo
    if os.path.exists(config_path):
        app.config.from_pyfile(config_path)

def prep_redis(app):
    # wipe the redis temp cache (not the non-temp one)
    client = redis.StrictRedis(host=app.config['REDIS_CACHE_HOST'], port=app.config['REDIS_CACHE_PORT'], db=app.config['REDIS_CACHE_DB'])
    client.flushdb()

def initialise_index(app):
    # refreshing the mappings and making all known licenses available
    # in the index are split out since the latter can take quite a while
    # but refreshing the mappings has to be done every time dao.DomainObject.delete_all() is called
    refresh_mappings(app)
    put_licenses_in_index(app)

def get_index_path(app):
    i = str(app.config['ELASTIC_SEARCH_HOST']).rstrip('/')
    i += '/' + app.config['ELASTIC_SEARCH_DB']
    return i

def refresh_mappings(app):
    i = get_index_path(app)
    mappings = app.config["MAPPINGS"]
    for key, mapping in mappings.iteritems():
        im = i + '/' + key + '/_mapping'
        exists = requests.get(im)
        if exists.status_code != 200:
            ri = requests.post(i)
            r = requests.put(im, json.dumps(mapping))
            print key, r.status_code

def put_licenses_in_index(app):
    i = get_index_path(app)
    # put the currently available licences into the licence index
    for l in licenses.LICENSES:
        r = requests.post(i + '/license/' + l, json.dumps(licenses.LICENSES[l]))

def setup_error_email(app):
    ADMINS = app.config.get('ADMINS', '')
    if not app.debug and ADMINS:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler('127.0.0.1',
                                   'server-error@no-reply.com',
                                   ADMINS, 'error')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

app = create_app()

