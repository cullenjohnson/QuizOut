from PySide6.QtCore import QObject, Signal

class GlobalKeyMonitorCommunicator(QObject):
    keypress = Signal(str)