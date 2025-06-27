from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from .sharedLogger import logger
import os

# init SQLAlchemy
db = SQLAlchemy()

socketio = SocketIO()

load_dotenv()

app = Flask(__name__)

api_secret_path = os.path.join(os.path.expanduser(os.getenv("SECRET_LOCATION")), "api_secret")
with open(api_secret_path, "r") as f:
    app.config['SECRET_KEY'] = f.read()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)

# blueprint for auth routes in our app
# from .auth import auth as auth_blueprint
# app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

socketio.init_app(app, async_mode="threading")

logger.info("SocketIO server started")