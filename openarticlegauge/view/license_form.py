import json
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SelectField, validators, FormField, FieldList
from wtforms.widgets import TableWidget
from wtforms.validators import Required, Length
from flask import Blueprint, request, redirect, url_for, abort, render_template, flash

from openarticlegauge.models import Publisher

blueprint = Blueprint('license_form', __name__)

@blueprint.route('/', methods=['GET','POST'])
@blueprint.route('/<publisher_id>', methods=['GET','POST'])
def publisher_license(publisher_id=None):
    p = Publisher.pull(publisher_id)
    form = PublisherLicenseForm(request.form, p)
       
    print json.dumps(form.data, indent=4)
    if request.method == 'POST' and form.validate():
        if not p:
            p = Publisher()
        
        form.populate_obj(p)
        print json.dumps(p.data, indent=4)
        p.save()
        return redirect(url_for('.publisher_license', publisher_id=p.id))
        
    return render_template('license_form.html', 
            form=form)

class LicenseForm(Form): 

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(LicenseForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)
    
    license_statement = TextAreaField('License Statement', [validators.required()])
    license_type = SelectField('Licenses', [validators.required()], choices=[('CC-By', 'CC-BY'), ('cc-nc', 'CC-NC'), ('cc-sa', 'CC-SA')])
    version = TextField('Version')
    example_doi = TextField('Example DOI', [validators.required(), validators.Regexp("^((http:\/\/){0,1}dx.doi.org/|(http:\/\/){0,1}hdl.handle.net\/|doi:|info:doi:){0,1}(?P<id>10\..+\/.+)")])
            
class PublisherLicenseForm(Form):
    publisher_name = TextField('Publisher Name', [validators.required()])
    journal_urls = FieldList(TextField('Journal URL',[validators.required(), validators.URL()]), min_entries=1)
    licenses = FieldList(FormField(LicenseForm), min_entries=1)
    

