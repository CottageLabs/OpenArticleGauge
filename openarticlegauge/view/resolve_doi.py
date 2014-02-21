import requests
from flask import Blueprint

blueprint = Blueprint('resolve_doi', __name__)

@blueprint.route('/<path:doi>', methods=['GET'])
def resolve_doi(doi):
    url = 'http://dx.doi.org/' + doi
    r = requests.head(url)
    if r.url != url:
        return r.url
    r = requests.get(url)
    if r.url != url:
        return r.url
    return "DOI could not be resolved." 
    
