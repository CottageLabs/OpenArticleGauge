import os, string
from functools import wraps
from flask import request, current_app
from random import choice

import requests
import logging
import magic
from time import sleep
import socket

from urlparse import urlparse, urljoin

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

from openarticlegauge import config
from openarticlegauge import models

log = logging.getLogger(__name__)
         
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    if ( test_url.scheme in ('http', 'https') and 
            ref_url.netloc == test_url.netloc ):
        return target
    else:
        return '/'

def send_mail(to, fro, subject, text, files=[],server=config.DEFAULT_HOST):
    assert type(to)==list
    assert type(files)==list
 
    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
 
    msg.attach( MIMEText(text) )
 
    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)
 
    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string() )
    smtp.close()


def jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function


# derived from http://flask.pocoo.org/snippets/45/ (pd) and customised
def request_wants_json():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']:
        best = True
    else:
        best = False
    if request.values.get('format','').lower() == 'json' or request.path.endswith(".json"):
        best = True
    return best
        
def generate_password(length=8):
    chars = string.letters + string.digits
    pw = ''.join(choice(chars) for _ in range(length))
    return pw

def http_stream_get(url):
    r = requests.get(url, stream=True, timeout=config.CONN_TIMEOUT)
    r.encoding = 'utf-8'

    size_limit = config.MAX_REMOTE_FILE_SIZE
    header_reported_size = r.headers.get("content-length")
    try:
        header_reported_size = int(header_reported_size)
    except Exception as e:
        header_reported_size = 0

    if header_reported_size > size_limit:
        return ''

    downloaded_bytes = 0
    content = ''
    chunk_no = 0
    attempt = 0
    retries = config.MAX_CONN_RETRIES
    while attempt <= retries:
        try:
            for chunk in r.iter_content(chunk_size=config.HTTP_CHUNK_SIZE):
                chunk_no += 1
                downloaded_bytes += len(bytes(chunk))

                if chunk_no == 1:
                    if magic.from_buffer(chunk).startswith('PDF'):
                        raise models.LookupException('File at {0} is a PDF according to the python-magic library. Not allowed!'.format(url))

                # check the size limit again
                if downloaded_bytes > size_limit:
                    raise models.LookupException('File at {0} is larger than limit of {1}'.format(url, size_limit))
                if chunk:  # filter out keep-alive new chunks
                    content += chunk
            break

        except socket.timeout:
            attempt += 1
            log.debug('Request to {url} timeout, attempt {attempt}'.format(url=url, attempt=attempt))

        sleep(2 ** attempt)

    r.connection.close()
    return r, content, downloaded_bytes

def http_get(url):
    attempt = 0
    retries = config.MAX_CONN_RETRIES
    r = None

    while attempt <= retries:
        try:
            r = requests.get(url, timeout=config.CONN_TIMEOUT)
            break
        except requests.exceptions.Timeout:
            attempt += 1
            log.debug('Request to {url} timeout, attempt {attempt}'.format(url=url, attempt=attempt))
        sleep(2 ** attempt)
    if r:
        r.encoding = 'utf-8'
    return r



