from flask import render_template
from . import main
# from .. import db

@main.route('/')
def index():
    return render_template('index.html')

