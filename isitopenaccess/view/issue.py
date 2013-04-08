# present and accept dispute processing

from flask import Blueprint, request, make_response, render_template, flash, redirect

from isitopenaccess.core import app
import isitopenaccess.util as util
import isitopenaccess.models as models

blueprint = Blueprint('issue', __name__)


@blueprint.route("/", methods=['GET','POST'])
@blueprint.route(".json", methods=['GET','POST'])
@blueprint.route("/<path:path>", methods=['GET','POST','DELETE'])
@util.jsonp
def issue(path=''):
    givejson = util.request_wants_json()
    path = path.replace('.json','')

    i = False
    
    if path:
        i = models.Issue.pull(path)

    if request.method == 'GET':
        if givejson:
            resp = make_response( i.data )
            resp.mimetype = "application/json"
            return resp
        else:
            return render_template('issue.html', issue=i)

    elif request.method == 'POST':
        if not i:
            i = models.Issue()

        if request.json:
            i.data = request.json
        elif request.values:
            i.data['about'] = request.values['about']
            i.data['issue'] = request.values['issue']
            i.data['email'] = request.values['email']
        else:
            abort(404)

        # only save an issue about an ID we actually have a record for
        if len(i.data['about']) < 9:
            cid = 'pmid:'
        else:
            cid = 'doi:'
        check = models.Record.pull(cid + i.data['about'].replace('/','_'))
        if check is not None:
            i.save()
        elif givejson:
            abort(404)
        else:
            flash("Sorry, your issue is about an identifier for which we do not hold a record.", 'error')
            return render_template('issue.html', issue=i)

        if app.config['CONTACT_EMAIL'] and not app.config['DEBUG']:
            text = 'Hey, an issue has been raised for ' + i.data['about'] + '\n\nView it at http://iioa.cottagelabs.com/issue/' + i.id
            util.send_mail([app.config['CONTACT_EMAIL']], app.config['CONTACT_EMAIL'], "issue raised", text)

        if givejson:
            resp = make_response( i.data )
            resp.mimetype = "application/json"
            return resp
        else:
            flash("Thanks, your issue has been raised", 'success')
            return redirect('/issue/' + i.id)

    elif request.method == 'DELETE' and i:
        i.delete()
        return ""
    else:
        abort(404)

