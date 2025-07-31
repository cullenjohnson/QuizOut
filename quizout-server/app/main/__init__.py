from flask import Blueprint

main_blueprint = Blueprint('main', __name__)
auth_blueprint = Blueprint('auth', __name__)
restapi_blueprint = Blueprint('restapi', __name__, url_prefix="/api")

from . import main, auth, events, restapi