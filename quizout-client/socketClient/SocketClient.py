import logging
import json
from socketio import AsyncClient
from utils.SocketClientCommunicator import SocketClientCommunicator

from . import ServerConfig

logger = logging.getLogger(__name__)

class SocketClient:
    callbacks = None

    def __init__(self, config:ServerConfig, socketClientCommunicator:SocketClientCommunicator):
        self.url = config.url

        self.sio = AsyncClient(handle_sigint=True)
        self.sio.connection_url = self.url
        self.sio.reconnection = config.reconnection
        self.sio.reconnection_attempts = config.reconnection_attempts
        self.sio.reconnection_delay = config.reconnection_delay
        self.sio.reconnection_delay_max = config.reconnection_delay_max

        self.socketClientComm = socketClientCommunicator

        self.setup_event_handlers()

    async def start(self):
        await self.connect()
        await self.sio.wait()

    def setup_event_handlers(self):
        @self.sio.event
        async def connect():
            logger.info(f"Connected to {self.url} . SID: {self.sio.sid}")
            self.socketClientComm.connected.emit()

        @self.sio.event
        async def disconnect():
            logger.info('Disconnected from server')
            self.socketClientComm.disconnected.emit()


        @self.sio.on('resetBuzzers')
        async def resetBuzzers(jsonData):
            data = json.loads(jsonData)
            logger.info(f"{self.url} reset the buzzers. {data}")
            self.socketClientComm.resetBuzzers.emit(data)

        @self.sio.on('buzzerTimeout')
        async def buzzerTimeout():
            logger.info(f"{self.url} says: buzzer timeout")
            self.socketClientComm.buzzerTimeout.emit()

        @self.sio.on('playerAnswering')
        async def playerAnswering(playerKey):
            logger.info(f"{self.url} says: player {playerKey} answering...")
            self.socketClientComm.playerAnswering.emit(playerKey)

        @self.sio.on('playerCorrect')
        async def playerCorrect(playerKey):
            logger.info(f"{self.url} says: player {playerKey} was correct!")
            self.socketClientComm.playerCorrect.emit(playerKey)

        @self.sio.on('playerIncorrect')
        async def playerIncorrect(playerKey):
            logger.info(f"{self.url} says: player {playerKey} was incorrect")
            self.socketClientComm.playerIncorrect.emit(playerKey)

    async def connect(self):
        try:
            await self.sio.connect(self.url)
        except Exception as e:
            logger.error(f"Failed to connect to {self.url}: {e}")
            raise

    async def disconnect(self):
        try:
            await self.sio.disconnect()
        except Exception as e:
            logger.error(f"Failed to disconnect from {self.url}: {e}")
            raise

    async def sendMessage(self, data=None):
        try:
            await self.sio.emit('message', data)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def playerBuzzed(self, playerKey:str):
        try:
            await self.sio.emit('playerBuzzed', playerKey)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
