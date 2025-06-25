from flask import Flask, render_template, request
from flask_socketio import SocketIO
from dotenv import load_dotenv
import logging
import logging.handlers
import os


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)


    os.makedirs(f'{os.path.expanduser("~")}/.quizoutserver/log', exist_ok=True)
    fileHandler = logging.handlers.TimedRotatingFileHandler(f'{os.path.expanduser("~")}/.quizoutserver/log/server.log', when='midnight', interval=1, backupCount=7)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)
    return logger


load_dotenv()

api_secret_path = os.path.join(os.path.expanduser(os.getenv("SECRET_LOCATION")), "api_secret")

logger = setup_logging()
app = Flask(__name__)
with open(api_secret_path, "r") as f:
    app.config['SECRET_KEY'] = f.read()
    logger.info(app.config['SECRET_KEY'][:1] + "********")

socketio = SocketIO(app, async_mode='threading')
logger.info("SocketIO server started")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.event
def connect(data = None):
    if data:
        logger.info(f'Client [sid {request.sid}] connected with data:', data)
    else:
        logger.info(f'Client [sid {request.sid}] connected')
    socketio.emit('response', 'Welcome to the QuizOut server!')

@socketio.event
def message(data = None):
    logger.debug(f'Client [sid {request.sid}] sent message:{data}.')
    socketio.emit('response', f'Server received message: {data}')

if __name__ == '__main__':
    socketio.run(app, debug=True)