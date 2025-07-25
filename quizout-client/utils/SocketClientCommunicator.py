from PySide6.QtCore import QObject, Signal

class SocketClientCommunicator(QObject):
    connected = Signal()
    disconnected = Signal()
    resetBuzzers = Signal(dict)
    buzzerTimeout = Signal()
    clientError = Signal(Exception)
    playerAnswering = Signal(str)
    playerCorrect = Signal(str)
    playerIncorrect = Signal(str)