import sys
import os
import configparser
import logging
import logging.handlers
import threading
import select
from PySide6.QtWidgets import QApplication
try:
    import evdev
    EVDEV_AVAILABLE = True
except ImportError:
    EVDEV_AVAILABLE = False

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

def start_global_key_monitor(keyPressHandler):
    """Start global keyboard monitoring using evdev in a separate thread"""
    if not EVDEV_AVAILABLE:
        logging.getLogger(__name__).warning("evdev not available, global key capture disabled")
        return
    
    def monitor_keyboards():
        logger = logging.getLogger(__name__)
        devices = []
        
        try:
            for path in evdev.list_devices():
                device = evdev.InputDevice(path)
                caps = device.capabilities()
                # Check if it's a keyboard
                if evdev.ecodes.EV_KEY in caps and evdev.ecodes.KEY_A in caps.get(evdev.ecodes.EV_KEY, []):
                    devices.append(device)
                    logger.info(f'Monitoring keyboard: {device.name}')
            
            if not devices:
                logger.warning('No keyboards found for global monitoring')
                return
            
            logger.info('Global keyboard monitoring started')
            while True:
                r, w, x = select.select(devices, [], [], 0.1)
                for device in r:
                    for event in device.read():
                        if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # Key press
                            try:
                                # Try to convert keycode to character
                                if event.code >= evdev.ecodes.KEY_1 and event.code <= evdev.ecodes.KEY_9:
                                    char = str(event.code - evdev.ecodes.KEY_1 + 1)
                                    keyPressHandler.handle_key_press(char)
                                elif event.code == evdev.ecodes.KEY_0:
                                    keyPressHandler.handle_key_press('0')
                                elif event.code >= evdev.ecodes.KEY_A and event.code <= evdev.ecodes.KEY_Z:
                                    char = chr(event.code - evdev.ecodes.KEY_A + ord('a'))
                                    keyPressHandler.handle_key_press(char)
                            except Exception as e:
                                logger.debug(f"Error processing key event: {e}")
        except Exception as e:
            logger.error(f"Global keyboard monitoring error: {e}")
    
    # Start monitoring in daemon thread
    thread = threading.Thread(target=monitor_keyboards, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    config = setup_app()
    app = QApplication(sys.argv)
    keyPressHandler = KeyPressHandler(TeamBuzzerInfo(config["team_buzzer_keys"]))
    
    # Start global keyboard monitoring
    start_global_key_monitor(keyPressHandler)
    
    window = MainWindow(config)
    window.show()
    keyPressHandler.connectCallback(window.on_buzzer_key_press)
    window.raise_()
    sys.exit(app.exec())
