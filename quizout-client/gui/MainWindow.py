import asyncio
import threading
import logging
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QComboBox

from .SoundEffectPlayer import SoundEffectPlayer
from socketClient.SocketClient import SocketClient
from socketClient.ServerConfig import ServerConfig
from data import ClientInfo, TeamBuzzerInfo
from utils.SocketClientCommunicator import SocketClientCommunicator
from utils.TieBreaker import TieBreaker
from utils.Enums import SoundEffect

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.connecting = False
        self.listening = False

        self.socketClientComm = SocketClientCommunicator()
        self.socketClientComm.connected.connect(self.on_connected)
        self.socketClientComm.disconnected.connect(self.on_disconnected)
        self.socketClientComm.clientError.connect(self.on_client_error)
        self.socketClientComm.resetBuzzers.connect(self.on_activate_buzzers)
        self.socketClientComm.buzzerTimeout.connect(self.on_buzzer_timeout)
        self.socketClientComm.playerAnswering.connect(self.on_player_answering)
        self.socketClientComm.playerCorrect.connect(self.on_player_correct)
        self.socketClientComm.playerIncorrect.connect(self.on_player_incorrect)

        self.teamBuzzerInfo = TeamBuzzerInfo(config["team_buzzer_keys"])
        self.clientInfo = ClientInfo(self.teamBuzzerInfo)

        self.socket_client = SocketClient(
            config = ServerConfig(config['server']),
            clientInfo = self.clientInfo,
            socketClientCommunicator = self.socketClientComm
        )

        self.tieBreaker = TieBreaker(self.teamBuzzerInfo)
        self.tieBreaker.playerChosen.connect(self.on_player_chosen)

        self.loop = asyncio.new_event_loop()
        self.new_client_thread()
        self.soundEffectPlayer = SoundEffectPlayer(self)

        self.init_ui()

    def new_client_thread(self):
        self.connecting = True
        self.client_thread = threading.Thread(target=self.start_loop, daemon=True)
        self.client_thread.start()

    def init_ui(self):
        self.setWindowTitle('Hello World')
        self.resize(800, 600)
        self.connectButton = QPushButton('Connect to Server', self)
        self.disconnectButton = QPushButton('Disconnect from Server', self)
        self.disconnectButton.setEnabled(False)
        
        self.soundEffectComboBox = QComboBox(self)
        self.soundEffectComboBox.addItem("Activate", SoundEffect.ActivateSound)
        self.soundEffectComboBox.addItem("Buzz", SoundEffect.BuzzSound)
        self.soundEffectComboBox.addItem("Correct", SoundEffect.CorrectSound)
        self.soundEffectComboBox.addItem("Incorrect", SoundEffect.IncorrectSound)
        self.soundEffectComboBox.addItem("Timeout", SoundEffect.TimeoutSound)
        self.testSoundButton = QPushButton('▶️ Test Sound', self)

        testAudioLayout = QHBoxLayout(self, spacing = 2)
        testAudioLayout.addWidget(self.soundEffectComboBox)
        testAudioLayout.addWidget(self.testSoundButton)

        centralWidget = QWidget(self)
        layout = QVBoxLayout(self, spacing=4)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        layout.addWidget(self.connectButton)
        layout.addWidget(self.disconnectButton)
        layout.addLayout(testAudioLayout)

        self.connectButton.clicked.connect(self.on_connect_click)
        self.disconnectButton.clicked.connect(self.on_disconnect_click)
        self.testSoundButton.clicked.connect(self.on_test_sound_click)

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.socket_client.start())
        except Exception as e:
                self.socketClientComm.clientError.emit(e)

    # SocketClient Signal handlers
    def on_client_error(self, e):
        self.connecting = False
        logger.error(f"Failed to connect to server: {e}")
        self.alertDialog = QMessageBox(self)
        self.alertDialog.setText(f"Failed to connect to server: {e}")
        self.alertDialog.setWindowTitle("Connection Error")
        self.alertDialog.exec()

    def on_connected(self):
        self.connecting = False
        logging.info("Connected to server!")
        self.clientConnected = True
        self.connectButton.setEnabled(False)
        self.disconnectButton.setEnabled(True)

    def on_disconnected(self):
        logging.info("Disconnected from server.")
        self.clientConnected = False
        self.connectButton.setEnabled(True)
        self.disconnectButton.setEnabled(False)

    def on_activate_buzzers(self, data:dict):
        logger.info(f"Listening to buzzers! {data}")
        self.soundEffectPlayer.playSound(SoundEffect.ActivateSound)
        self.inactiveTeams = data.get("inactive_teams", [])
        self.listening = True

    def on_buzzer_timeout(self):
        if self.listening:
            logger.info("Buzzers timed out")
            self.listening = False
            self.soundEffectPlayer.playSound(SoundEffect.TimeoutSound)

    def on_player_answering(self, playerKey:str):
        logger.info(f"Player answering: {playerKey}")
        self.soundEffectPlayer.playSound(SoundEffect.BuzzSound)

    def on_player_correct(self, playerKey:str):
        logger.info(f"Player Correct: {playerKey}")
        self.soundEffectPlayer.playSound(SoundEffect.CorrectSound)

    def on_player_incorrect(self, playerKey:str):
        logger.info(f"Player incorrect: {playerKey}")
        self.soundEffectPlayer.playSound(SoundEffect.IncorrectSound)

        # Reactivate buzzers for other teams
        self.inactiveTeams.append(self.teamBuzzerInfo.buzzerTeams[playerKey])
        if len(self.inactiveTeams) != len(self.teamBuzzerInfo.teams):
            self.listening = True


    # TieBreaker Signal handlers
    def on_player_chosen(self, keyPressInfo):
        self.listening = False
        (team, key, timestamp) = keyPressInfo
        logger.info(f"Player chosen {keyPressInfo}")
        try:
            asyncio.run_coroutine_threadsafe(
                self.socket_client.playerBuzzed(key),
                self.loop)
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            self.alertDialog = QMessageBox(self)
            self.alertDialog.setText(f"Failed to connect to server: {e}")
            self.alertDialog.setWindowTitle("Connection Error")
            self.alertDialog.exec()


    # GUI Event handlers
    def closeEvent(self, event):
        asyncio.run_coroutine_threadsafe(self.socket_client.disconnect(), self.loop)
        event.accept()

    # def on_send_click(self):
    #     logger.info('Button clicked, sending message to server...')
    #     try:
    #         asyncio.run_coroutine_threadsafe(
    #             self.socket_client.sendMessage('Hello from the client!'),
    #             self.loop)
    #     except Exception as e:
    #         logger.error(f"Failed to connect to server: {e}")
    #         self.alertDialog = QMessageBox(self)
    #         self.alertDialog.setText(f"Failed to connect to server: {e}")
    #         self.alertDialog.setWindowTitle("Connection Error")
    #         self.alertDialog.exec()

    def on_connect_click(self):
        if not self.connecting:
            logger.info('Connecting to server...')
            self.new_client_thread()

    def on_disconnect_click(self):
        logger.info('Disconnecting from server...')
        try:
            asyncio.run_coroutine_threadsafe(
                self.socket_client.disconnect(),
                self.loop
            )
        except Exception as e:
            logger.error(f"Failed to disconnect from server: {e}")
            self.alertDialog = QMessageBox(self)
            self.alertDialog.setText(f"Failed to disconnect from server: {e}")
            self.alertDialog.setWindowTitle("DisconnectionError")
            self.alertDialog.exec()

    def on_test_sound_click(self):
        effect = self.soundEffectComboBox.currentData()
        self.soundEffectPlayer.playSound(effect)

    # Other methods
    def on_buzzer_key_press(self, keyPressInfo):
        if self.listening:
            self.tieBreaker.activate(keyPressInfo, self.inactiveTeams)