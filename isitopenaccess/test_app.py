from flask import url_for
from app import app

with app.test_request_context():
    print url_for('lookup', ids="assad,asdasd,asd")
