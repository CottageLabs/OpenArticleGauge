import json
from time import sleep
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SelectField, validators, FormField, FieldList
from flask import Blueprint, request, redirect, url_for, abort, render_template, flash

from openarticlegauge.models import LicenseStatement
from openarticlegauge.licenses import licenses_dropdown, LICENSES

blueprint = Blueprint('license_statement', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/list', methods=['GET', 'POST'])
def list_statements():
    statements = LicenseStatement.all(sort=[{"license_type" : {"order" : "asc"}}])

    if request.method == 'POST':
        for key in request.form:
            if key.startswith('delete_statement'):
                which = key.split('-')[1]
                ls = LicenseStatement.pull(which)
                if ls:
                    ls.delete()
                    sleep(1.5)  # ugly hack, make sure statement is saved before showing to user
                    statements = LicenseStatement.all(sort=[{"license_type" : {"order" : "asc"}}])

    return render_template('statements.html', statements=statements, license_info=LICENSES)

@blueprint.route('/new', methods=['GET','POST'])
@blueprint.route('/<statement_id>', methods=['GET','POST'])
def statement_edit(statement_id=None):
    ls = LicenseStatement.pull(statement_id)
    form = LicenseForm(request.form, ls)
       
    if request.method == 'POST' and form.validate():
        if not ls:
            ls = LicenseStatement()
        ls.license_statement = form.license_statement.data
        ls.license_type = form.license_type.data
        if form.version.data:
            ls.version = form.version.data
        if form.example_doi.data:
            ls.example_doi = form.example_doi.data
        print json.dumps(ls.data, indent=4)
        ls.save()
        sleep(1.5)  # ugly hack, make sure statement is saved before showing to user
        return redirect(url_for('.list_statements', _anchor=ls.edit_id))
        
    return render_template('statement.html', form=form)

class LicenseForm(Form): 
    
    license_statement = TextAreaField('License Statement', [validators.required()])
    license_type = SelectField('Licenses', [validators.required()], choices=licenses_dropdown)
    version = TextField('Version')
    example_doi = TextField('Example DOI', [validators.Optional(), validators.Regexp("^((http:\/\/){0,1}dx.doi.org/|(http:\/\/){0,1}hdl.handle.net\/|doi:|info:doi:){0,1}(?P<id>10\..+\/.+)")])
            
class MultipleStatementsForm(Form):
    licenses = FieldList(FormField(LicenseForm), min_entries=1)
