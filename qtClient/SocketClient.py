import logging
from socketio import AsyncClient

class SocketClient:
    callbacks = None

    def __init__(self, config, on_message=None, on_connect=None, on_disconnect=None):
        self.logger = logging.getLogger()
        url = config.get('url', 'http://localhost:5000')

        self.sio = AsyncClient(handle_sigint=True)
        self.sio.connection_url = url
        self.sio.reconnection = config.getboolean('reconnection', True)
        self.sio.reconnection_attempts = config.getint('reconnection_attempts', 5)
        self.sio.reconnection_delay = config.getint('reconnection_delay', 1)
        self.sio.reconnection_delay_max = config.getint('reconnection_delay_max', 5)

        self.url = url

        self.on_message = on_message if on_message else lambda data: self.logger.info(f"Message received: {data}")
        self.on_connect = on_connect if on_connect else lambda: self.logger.info("Connected to server")
        self.on_disconnect = on_disconnect if on_disconnect else lambda: self.logger.info("Disconnected from server")

        self.setup_event_handlers()

    async def start(self):
        await self.connect()
        await self.sio.wait()

    def setup_event_handlers(self):
        @self.sio.event
        async def connect():
            self.logger.info(f"Connected to {self.url} . SID: {self.sio.sid}")
            self.on_connect()

        @self.sio.event
        async def disconnect():
            self.logger.info('Disconnected from server')
            self.on_disconnect

        @self.sio.on('response')
        async def response(message=None):
            self.logger.info(f"{self.url} said: {message}")
            self.on_message(message)

        # @self.sio.on('*')
        # async def any_event(event, sid, data=None):
        #     self.logger.info(f"Event: {event}, SID: {sid}, Data: {data}")

    async def connect(self):
        try:
            await self.sio.connect(self.url)
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.url}: {e}")
            raise

    async def disconnect(self):
        try:
            await self.sio.disconnect()
        except Exception as e:
            self.logger.error(f"Failed to disconnect from {self.url}: {e}")
            raise

    async def sendMessage(self, data=None):
        try:
            await self.sio.emit('message', data)
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise