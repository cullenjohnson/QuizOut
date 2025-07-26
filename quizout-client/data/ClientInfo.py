import socket
from uuid import UUID, uuid4

from .TeamBuzzerInfo import TeamBuzzerInfo

class ClientInfo:
    ip:str
    uuid:UUID
    teamBuzzerInfo:TeamBuzzerInfo

    def __init__(self, teamBuzzerInfo:TeamBuzzerInfo):
        self.uuid = uuid4()

        hostname = socket.gethostname()
        self.ip = socket.gethostbyname(hostname)

        self.teamBuzzerInfo = teamBuzzerInfo