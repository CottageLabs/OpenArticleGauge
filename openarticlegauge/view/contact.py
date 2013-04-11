'''
A contact-form backend mailer endpoint
'''

from flask import Blueprint, request, abort, render_template, flash

from openarticlegauge.core import app
import openarticlegauge.util as util


blueprint = Blueprint('contact', __name__)


# catch mailer requests and send them on
@blueprint.route('/', methods=['GET','POST'])
def mailer():
    if request.method == 'GET':
        return render_template('contact.html')

    elif request.method == 'POST':
        if app.config['CONTACT_EMAIL'] and not app.config['DEBUG'] and request.values.get('message',False) and not request.values.get('not',False):
            util.send_mail(
                [app.config['CONTACT_EMAIL'] + '>'],
                app.config['CONTACT_EMAIL'],
                'HOII enquiry',
                request.values['message']
            )
            flash('Thanks, your query will be processed soon.', 'success')
            return render_template('contact.html')
        else:
            flash('Sorry, your request was missing something, or we have not enabled the contact form...')
            return render_template('contact.html')

 

