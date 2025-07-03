from PySide6.QtCore import QObject, Signal

class SocketClientCommunicator(QObject):
    connected = Signal()
    disconnected = Signal()
    messageReceived = Signal(str)
    clientError = Signal(Exception)