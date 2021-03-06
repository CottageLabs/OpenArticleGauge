from flask import Blueprint, request, make_response, render_template, abort

import json, logging

from openarticlegauge import workflow, config
from openarticlegauge import util

LOG_FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)

blueprint = Blueprint('lookup', __name__)

@blueprint.route('/', methods=['GET','POST'])
@blueprint.route(".json", methods=['GET','POST'])
@blueprint.route("/<path:path>", methods=['GET','POST'])
@util.jsonp
def api_lookup(path='',ids=[]):
    givejson = util.request_wants_json()
    path = path.replace('.json','')
    idlimit = config.LOOKUP_LIMIT
    
    # have we been asked to prioritise?
    priority = bool(request.values.get("priority", False))
    if priority:
        idlimit = config.PRIORITY_LOOKUP_LIMIT
    
    idlist = []

    # look for JSON in the incoming request data
    if request.json:
        # the MIME type of the request is set properly - this is how it
        # should be
        request_json = request.json
    else:
        request_json = None

        # check if somebody just POST-ed without bothering to request
        # the right MIME type
        try:
            request_json = json.loads(request.data)
        except ValueError:
            pass

        # now check if the client mislabeled the request really badly,
        # i.e. saying it's HTML form data when it's actually JSON
        try:
            request_json = json.loads(str(request.form))
        except ValueError:
            pass

    if ids and isinstance(ids,basestring):
        idlist = [ {"id":i} for i in ids.split(',') ]
    elif ids:
        for i in ids:
            if isinstance(i,basestring):
                idlist.append({"id":i})
            else:
                idlist.append(i)
    elif request_json:
        for item in request_json:
            if isinstance(item,dict):
                idlist.append(item)
            else:
                idlist.append({"id":item})
    elif path and len(path) > 0:
        idlist = [ {"id":i} for i in path.split(',') ]

    log.debug('LOOKUP: About to do a request size test. Len of idlist: ' + str(len(idlist)))
    if len(idlist) > idlimit:
        abort(400)

    if idlist:
        results = workflow.lookup(idlist, priority).json()
    else:
        results = json.dumps({})

    if request.method == 'GET' and not givejson:
        if path:
            triggered = idlist
        else:
            triggered = False
        return render_template('index.html', results=results, triggered=triggered)
    else:
        resp = make_response( results )
        resp.mimetype = "application/json"
        return resp

