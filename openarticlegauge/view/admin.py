from flask import Blueprint, request, make_response, render_template, flash, redirect
from flask.ext.login import login_required

from openarticlegauge.core import app
import openarticlegauge.util as util
import openarticlegauge.models as models
import openarticlegauge.invalidate as inval

import json

blueprint = Blueprint('admin', __name__)

@blueprint.route("/")
@login_required
def index():
    return render_template("admin/index.html")

@blueprint.route("/invalidate")
@login_required
@util.jsonp
def invalidate():
    qy = request.values.get("source")
    j = json.loads(qy)
    
    # extract only the "query" from the source - we're not interested in the users facet, size, sort parameters, etc
    query = j.get("query")
    
    # we also need the "license_type", "handler" and "handler_version" from a query which looks something like:
    # {"query":{"bool":{"must":[{"term":{"license.type.exact":"failed-to-obtain-license"}},{"term":{"license.provenance.handler.exact":"ubiquitous"}}]}},"size":25}
    terms = [t.get("term") for t in query.get("bool", {}).get("must", []) if t.get("term") is not None]
    
    fields = {
        "license.type.exact" : "license_type", 
        "license.provenance.handler.exact" : "handler", 
        "license.provenance.handler_version.exact" : "handler_version"
    }
    
    args = {}
    for term in terms:
        k = term.keys()[0]
        v = term.values()[0]
        args[fields.get(k)] = v
    
    # use the query the user specified to get the records to invalidate
    # and pass the parameters of the licences to remove
    query = {"query" : query}
    inval.invalidate_license_by_query(query, **args)
    
    resp = make_response(json.dumps(args))
    resp.mimetype = "application/json"
    return resp
