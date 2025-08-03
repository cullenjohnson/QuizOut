from flask import render_template
from flask_login import login_required
from . import main_blueprint as main
from datetime import datetime, UTC

@main.route('/')
@login_required
def index():
    return render_template('index.html', current_time=datetime.now(UTC).timestamp() )