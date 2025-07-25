from flask import render_template
from flask_login import login_required, current_user
from . import main_blueprint as main
from .. import db

@main.route('/')
@login_required
def index():
    return render_template('index.html')