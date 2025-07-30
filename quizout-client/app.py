import sys
import os
import configparser
import logging
import logging.handlers
from PySide6.QtWidgets import QApplication

from utils import KeyPressHandler
from gui import MainWindow
from data import TeamBuzzerInfo

default_config = {
        'server': {
            'url': 'http://localhost:8000',
            'reconnection': 'True',
            'reconnection_attempts': '5',
            'reconnection_delay': '1',
            'reconnection_delay_max': '5'
        },
        'logging': {
            'level': 'DEBUG',
            'console_handler': 'True',
            'file_handler': 'True',
            'log_backup_count': '7'
        },
        "team_buzzer_keys": {
            "team1": "1,2,3",
            "team2": "4,5,6"
        },
        'buzzerSystem': {
            'tieThresholdMS': 2
        }
}

def setup_app():
    os.makedirs(f'{os.path.expanduser("~")}/.quizoutclient/log', exist_ok=True)

    config = get_config()
    loggingConfig = config['logging']

    logger = logging.getLogger()

    loggingLevel = loggingConfig.get('level', fallback='DEBUG').upper()

    logger.setLevel(loggingLevel)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if loggingConfig.getboolean('console_handler', fallback=True):
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(loggingLevel)
        consoleHandler.setFormatter(formatter)

        logger.addHandler(consoleHandler)

    if loggingConfig.getboolean('file_handler', fallback=True):
        fileHandler = logging.handlers.TimedRotatingFileHandler(
            f'{os.path.expanduser("~")}/.quizoutclient/log/client.log',
            when='midnight',
            interval=1,
            backupCount=loggingConfig.getint('log_backup_count', fallback=7))

        fileHandler.setLevel(loggingLevel)
        fileHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)


    return config

def get_config():
    config = configparser.ConfigParser()
    config_path = os.path.expanduser("~/.quizoutclient/client-config.ini")

    if not os.path.exists(config_path):
        os.makedirs(os.path.expanduser('~/.quizoutclient'), exist_ok=True)
        with open(config_path, 'w') as configfile:
            config.read_dict(default_config)
            config.write(configfile)
        return config

    config.read(config_path)
    return config

if __name__ == "__main__":
    config = setup_app()
    app = QApplication(sys.argv)
    keyPressHandler = KeyPressHandler(TeamBuzzerInfo(config["team_buzzer_keys"]))
    app.installEventFilter(keyPressHandler)
    window = MainWindow(config)
    window.show()
    keyPressHandler.connectCallback(window.on_buzzer_key_press)
    window.raise_()
    sys.exit(app.exec())
