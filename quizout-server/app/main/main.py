from flask import render_template
from . import main_blueprint as main
from .. import db

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')