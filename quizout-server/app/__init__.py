from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from .sharedLogger import logger
import os

# init SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

load_dotenv()

def create_app():
    app = Flask(__name__)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    api_secret_path = os.path.join(os.path.expanduser(os.getenv("SECRET_LOCATION")), "api_secret")
    with open(api_secret_path, "r") as f:
        app.config['SECRET_KEY'] = f.read()

    db_path = os.path.expanduser(os.getenv("SQLITE_PATH", "/data/db.sqlite"))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    db.init_app(app)
    migrate.init_app(app, db)

    # blueprint for auth routes in our app
    from .main import auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app, async_mode="threading")

    logger.info("SocketIO server started")

    return app