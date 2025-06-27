import logging
import logging.handlers
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("quizout_server")

os.makedirs(f'{os.path.expanduser("~")}/.quizoutserver/log', exist_ok=True)

logger.setLevel(logging.DEBUG if os.getenv('DEBUG') == 'True' else logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

consoleHandler = logging.StreamHandler()
# consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)

fileHandler = logging.handlers.TimedRotatingFileHandler(f'{os.path.expanduser("~")}/.quizoutserver/log/server.log', when='midnight', interval=1, backupCount=7)
# fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatter)

logger.addHandler(consoleHandler)
logger.addHandler(fileHandler)
    