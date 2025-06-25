import sys
import os
import configparser
import asyncio
import threading
import logging
import logging.handlers
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Signal, QObject

from SocketClient import SocketClient

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

class Communicator(QObject):
    connected = Signal()
    disconnected = Signal()
    messageReceived = Signal(str)

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.logger = logging.getLogger()

        self.comm = Communicator()
        self.comm.connected.connect(self.on_connected)
        self.comm.disconnected.connect(self.on_disconnected)
        self.comm.messageReceived.connect(self.on_message)

        self.socket_client = SocketClient(
            config=config['server'],
            on_connect=self.comm.connected.emit,
            on_disconnect=self.comm.disconnected.emit,
            on_message=self.comm.messageReceived.emit
        )

        self.loop = asyncio.new_event_loop()
        self.client_thread = threading.Thread(target=self.start_loop, daemon=True)
        self.client_thread.start()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Hello World')
        self.resize(800, 600)
        self.connectButton = QPushButton('Connect to Server', self)
        self.disconnectButton = QPushButton('Disconnect from Server', self)
        self.disconnectButton.setEnabled(False)
        self.sendButton = QPushButton('Send Message', self)
        self.sendButton.setEnabled(False)

        centralWidget = QWidget(self)
        layout = QVBoxLayout(self, spacing=10)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        layout.addWidget(self.connectButton)
        layout.addWidget(self.disconnectButton)
        layout.addWidget(self.sendButton)

        self.connectButton.clicked.connect(self.on_connect_click)
        self.disconnectButton.clicked.connect(self.on_disconnect_click)
        self.sendButton.clicked.connect(self.on_send_click)

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.socket_client.start())

    def on_connected(self):
        self.clientConnected = True
        self.connectButton.setEnabled(False)
        self.disconnectButton.setEnabled(True)
        self.sendButton.setEnabled(True)

    def on_disconnected(self):
        self.clientConnected = False
        self.connectButton.setEnabled(True)
        self.disconnectButton.setEnabled(False)
        self.sendButton.setEnabled(False)

    def on_message(self, msg):
        self.logger.info(f"Message received: {msg}")

    def closeEvent(self, event):
        asyncio.run_coroutine_threadsafe(self.socket_client.disconnect(), self.loop)
        event.accept()

    def on_send_click(self):
        self.logger.info('Button clicked, sending message to server...')
        try:
            asyncio.run_coroutine_threadsafe(
                self.socket_client.sendMessage('Hello from the client!'),
                self.loop)
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")
            self.alertDialog = QMessageBox(self)
            self.alertDialog.setText(f"Failed to connect to server: {e}")
            self.alertDialog.setWindowTitle("Connection Error")
            self.alertDialog.exec()

    def on_connect_click(self):
        self.logger.info('Connecting to server...')
        try:
            self.start_loop()
            self.logger.info('Connected to server!')
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")
            self.alertDialog = QMessageBox(self)
            self.alertDialog.setText(f"Failed to connect to server: {e}")
            self.alertDialog.setWindowTitle("Connection Error")
            self.alertDialog.exec()

    def on_disconnect_click(self):
        self.logger.info('Disconnecting from server...')
        try:
            asyncio.run_coroutine_threadsafe(
                self.socket_client.disconnect(),
                self.loop
            )
            self.logger.info('Disconnected from server!')
        except Exception as e:
            self.logger.error(f"Failed to disconnect from server: {e}")
            self.alertDialog = QMessageBox(self)
            self.alertDialog.setText(f"Failed to disconnect from server: {e}")
            self.alertDialog.setWindowTitle("DisconnectionError")
            self.alertDialog.exec()


if __name__ == "__main__":
    config = setup_app()
    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec())
