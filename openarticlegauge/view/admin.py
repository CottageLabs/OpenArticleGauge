from flask import Blueprint, request, make_response, render_template, flash, redirect

from openarticlegauge.core import app
import openarticlegauge.util as util
import openarticlegauge.models as models

blueprint = Blueprint('admin', __name__)

@blueprint.route("/")
def index():
    return render_template("admin/index.html")
