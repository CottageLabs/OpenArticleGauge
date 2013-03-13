# present and accept dispute processing

from flask import Blueprint, request, make_response, render_template

from isitopenaccess.core import app
import isitopenaccess.util as util
import isitopenaccess.models as models

blueprint = Blueprint('dispute', __name__)


@blueprint.route("/", methods=['GET','POST'])
@blueprint.route(".json", methods=['GET','POST'])
#@blueprint.route("/dispute/", methods=['GET','POST'])
@blueprint.route("/<path:path>", methods=['GET','POST'])
@util.jsonp
def disp(path=''):
    givejson = util.request_wants_json()
    path = path.replace('.json','')

    d = {}
    
    if path:
        d = models.Dispute.pull(path)

    if request.method == 'GET':
        return render_template('dispute.html', dispute=d)
    elif request.method == 'POST':
        if not d and request.json:
            d = models.Dispute(**request.json)
        else:
            # add to the dispute and save
            pass
        # should email someone here too perhaps
        if app.config['contact_email']:
            pass
        resp = make_response( results )
        resp.mimetype = "application/json"
        return resp
    else:
        abort(404)

