import sys
import os
import asyncio
import threading
import logging
import logging.handlers
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PySide6.QtCore import Signal, QObject

from SocketClient import SocketClient

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)


    os.makedirs(f'{os.path.expanduser("~")}/.socketClient/log', exist_ok=True)
    fileHandler = logging.handlers.TimedRotatingFileHandler(f'{os.path.expanduser("~")}/.socketClient/log/client.log', when='midnight', interval=1, backupCount=7)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

class Communicator(QObject):
    connected = Signal()
    disconnected = Signal()
    messageReceived = Signal(str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger()

        self.comm = Communicator()
        self.comm.connected.connect(self.on_connected)
        self.comm.disconnected.connect(self.on_disconnected)
        self.comm.messageReceived.connect(self.on_message)

        self.socket_client = SocketClient(
            url="http://localhost:5000",
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
    setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
