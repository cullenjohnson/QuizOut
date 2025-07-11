from PySide6.QtCore import QObject, Signal

class SocketClientCommunicator(QObject):
    connected = Signal()
    disconnected = Signal()
    messageReceived = Signal(str)
    resetBuzzers = Signal(dict)
    clientError = Signal(Exception)