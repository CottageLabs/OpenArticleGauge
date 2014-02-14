import json
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SelectField, validators
from wtforms.widgets import TableWidget
from wtforms.validators import Required, Length
from flask import Blueprint, request, abort, render_template, flash

from openarticlegauge.models import Publisher

blueprint = Blueprint('license_form', __name__)

@blueprint.route('/', methods=['GET','POST'])
def publisher_license():
    
    form = PublisherLicense()
    
    if request.method == 'POST' and form.validate():
        p = Publisher()
        print json.dumps(form.data, indent=4)
        form.populate_obj(p)
        p.publisher_name = "lala"
        print p.publisher_name
        print json.dumps(p.data, indent=2)
        #Save object
        #Redirect
        
    return render_template('license_form.html', 
            form = form)

class PublisherLicense(Form):
    publisher_name = TextField('Publisher Name', [validators.required()])
    journal_url = TextField('Journal URL',[validators.required(), validators.URL()])
    license_statement = TextAreaField('License Statement', [validators.required()])
    license_type = SelectField('Licenses', [validators.required()], choices=[('CC-By', 'CC-BY'), ('cc-nc', 'CC-NC'), ('cc-sa', 'CC-SA')])
    version = TextField('Version')
    example_doi = TextField('Example DOI', [validators.required(), validators.Regexp("^((http:\/\/){0,1}dx.doi.org/|(http:\/\/){0,1}hdl.handle.net\/|doi:|info:doi:){0,1}(?P<id>10\..+\/.+)")])
    

