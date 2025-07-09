import logging
from socketio import AsyncClient

from . import ServerConfig

logger = logging.getLogger(__name__)

class SocketClient:
    callbacks = None

    def __init__(self, config:ServerConfig, on_message=None, on_connect=None, on_disconnect=None, on_reset_buzzers=None):
        self.url = config.url

        self.sio = AsyncClient(handle_sigint=True)
        self.sio.connection_url = self.url
        self.sio.reconnection = config.reconnection
        self.sio.reconnection_attempts = config.reconnection_attempts
        self.sio.reconnection_delay = config.reconnection_delay
        self.sio.reconnection_delay_max = config.reconnection_delay_max

        self.on_message = on_message if on_message else lambda data: logger.info(f"Message received: {data}")
        self.on_connect = on_connect if on_connect else lambda: logger.info("Connected to server")
        self.on_disconnect = on_disconnect if on_disconnect else lambda: logger.info("Disconnected from server")
        self.on_reset_buzzers = on_reset_buzzers if on_reset_buzzers else lambda: logger.info("Reset buzzers")

        self.setup_event_handlers()

    async def start(self):
        await self.connect()
        await self.sio.wait()

    def setup_event_handlers(self):
        @self.sio.event
        async def connect():
            logger.info(f"Connected to {self.url} . SID: {self.sio.sid}")
            self.on_connect()

        @self.sio.event
        async def disconnect():
            logger.info('Disconnected from server')
            self.on_disconnect()

        @self.sio.on('response')
        async def response(message=None):
            logger.info(f"{self.url} said: {message}")
            self.on_message(message)

        @self.sio.on('resetBuzzers')
        async def resetBuzzers():
            logger.info(f"{self.url} reset the buzzers")
            self.on_reset_buzzers()
        # @self.sio.on('*')
        # async def any_event(event, sid, data=None):
        #     logger.info(f"Event: {event}, SID: {sid}, Data: {data}")

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