from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SelectField, validators
from wtforms.widgets import TableWidget
from wtforms.validators import Required, Length
from flask import Blueprint, request, abort, render_template, flash


blueprint = Blueprint('license_form', __name__)

@blueprint.route('/', methods=['GET','POST'])
def publisher_license():
    
    form = PublisherLicense()
    return render_template('license_form.html', 
            form = form)

class PublisherLicense(Form):
    publisher_name = TextField('Publisher Name', [validators.required()])
    journal_url = TextField('Journal URL',[validators.required(), validators.URL()])
    license_statement = TextAreaField('License Statement', [validators.required()])
    license = SelectField('Licenses', [validators.required()], choices=[('CC-By', 'CC-BY'), ('cc-nc', 'CC-NC'), ('cc-sa', 'CC-SA')])
    version = TextField('Version')
    example_DOI = TextField('Example DOI', [validators.required(), validators.Regexp("^((http:\/\/){0,1}dx.doi.org/|(http:\/\/){0,1}hdl.handle.net\/|doi:|info:doi:){0,1}(?P<id>10\..+\/.+)")])
    

