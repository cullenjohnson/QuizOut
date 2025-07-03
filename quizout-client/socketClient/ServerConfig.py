class ServerConfig:
    def __init__(self, serverConfig):
        self.url = serverConfig.get('url', 'http://localhost:5000')
        self.reconnection = serverConfig.getboolean('reconnection', True)
        self.reconnection_attempts = serverConfig.getint('reconnection_attempts', 5)
        self.reconnection_delay = serverConfig.getint('reconnection_delay', 1)
        self.reconnection_delay_max = serverConfig.getint('reconnection_delay_max', 5)