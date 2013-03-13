# present and accept dispute processing

from flask import Blueprint, request, make_response, render_template, flash, redirect

from isitopenaccess.core import app
import isitopenaccess.util as util
import isitopenaccess.models as models

blueprint = Blueprint('dispute', __name__)


@blueprint.route("/", methods=['GET','POST'])
@blueprint.route(".json", methods=['GET','POST'])
#@blueprint.route("/dispute/", methods=['GET','POST'])
@blueprint.route("/<path:path>", methods=['GET','POST','DELETE'])
@util.jsonp
def disp(path=''):
    givejson = util.request_wants_json()
    path = path.replace('.json','')

    d = False
    
    if path:
        d = models.Dispute.pull(path)

    if request.method == 'GET':
        if givejson:
            resp = make_response( d.data )
            resp.mimetype = "application/json"
            return resp
        else:
            return render_template('dispute.html', dispute=d)

    elif request.method == 'POST':
        if not d:
            d = models.Dispute()

        if request.json:
            d.data = request.json
        elif request.values:
            d.data['about'] = request.values['about']
            d.data['dispute'] = request.values['dispute']
            d.data['email'] = request.values['email']
        else:
            abort(404)

        # only save a dispute about an ID we actually have a record for
        if len(d.data['about']) < 9:
            cid = 'pmid:'
        else:
            cid = 'doi:'
        check = models.Record.pull(cid + d.data['about'].replace('/','_'))
        if check is not None:
            d.save()
        elif givejson:
            abort(404)
        else:
            flash("Sorry, your dispute is about an identifier for which we do not hold a record.", 'error')
            return render_template('dispute.html', dispute=d)

        if app.config['CONTACT_EMAIL'] and not app.config['DEBUG']:
            text = 'Hey, a dispute has been raised for ' + d + '\n\nView it at http://iioa.cottagelabs.com/dispute/' + d.id
            util.send_mail([app.config['CONTACT_EMAIL']], app.config['CONTACT_EMAIL'], "dispute raised", text)

        if givejson:
            resp = make_response( d.data )
            resp.mimetype = "application/json"
            return resp
        else:
            flash("Thanks, your dispute has been raised", 'success')
            #return render_template('dispute.html', dispute=d)
            return redirect('/dispute/' + d.id)

    elif request.method == 'DELETE' and d:
        d.delete()
        return ""
    else:
        abort(404)

