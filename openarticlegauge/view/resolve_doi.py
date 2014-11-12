import requests
from flask import Blueprint
from openarticlegauge import util
from openarticlegauge import config

blueprint = Blueprint('resolve_doi', __name__)

@blueprint.route('/<path:doi>', methods=['GET'])
def resolve_doi(doi):
    url = 'http://dx.doi.org/' + doi
    r = requests.head(url, timeout=config.CONN_TIMEOUT)
    if r.url != url:
        return r.url
    r, not_used_content, not_used_length = util.http_get(url)
    if r.url != url:
        return r.url
    return "DOI could not be resolved." 
    
