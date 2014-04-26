import json
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SelectField, validators, FormField, FieldList
from flask import Blueprint, request, redirect, url_for, render_template

from openarticlegauge.models import Publisher, LicenseStatement
from openarticlegauge.licenses import licenses_dropdown
from openarticlegauge import plugin

blueprint = Blueprint('publisher', __name__)


@blueprint.route('/', methods=['GET'])
@blueprint.route('/list', methods=['GET'])
def list_publishers():
    descriptions = plugin.PluginFactory.list_plugins("license_detect", sort_for_display=True)
    return render_template('publishers.html', plugins=descriptions)

@blueprint.route('/new', methods=['GET','POST'])
@blueprint.route('/<publisher_id>', methods=['GET','POST'])
def publisher_edit(publisher_id=None):
    p = Publisher.pull(publisher_id)
    form = PublisherLicenseForm(request.form, p)

    if request.method == 'POST' and form.validate():
        if not p:
            p = Publisher()
        p.publisher_name = form.publisher_name.data
        p.journal_urls = form.journal_urls.data
        p.licenses = form.licenses.data
        for l in p.licenses:
            new_ls = LicenseStatement(**l)
            new_ls.save()
        p.save()
        return redirect(url_for('.publisher_edit', publisher_id=p.id))
        
    return render_template('publisher.html', form=form)

class LicenseForm(Form): 

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(LicenseForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)
    
    license_statement = TextAreaField('License Statement', [validators.required()])
    license_type = SelectField('Licenses', [validators.required()], choices=licenses_dropdown)
    version = TextField('Version')
    example_doi = TextField('Example DOI', [validators.required(), validators.Regexp("^((http:\/\/){0,1}dx.doi.org/|(http:\/\/){0,1}hdl.handle.net\/|doi:|info:doi:){0,1}(?P<id>10\..+\/.+)")])
            
class PublisherLicenseForm(Form):
    publisher_name = TextField('Publisher Name', [validators.required()])
    journal_urls = FieldList(TextField('Journal URL',[validators.required(), validators.URL()]), min_entries=1)
    licenses = FieldList(FormField(LicenseForm), min_entries=1)
    

