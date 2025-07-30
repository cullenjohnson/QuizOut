import logging
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QKeyEvent, Qt
from collections.abc import Callable

from data import TeamBuzzerInfo

logger = logging.getLogger(__name__)

class KeyPressHandler(QObject):

    def __init__(self, teamBuzzerInfo:TeamBuzzerInfo):
        self.teamBuzzerInfo = teamBuzzerInfo
        self.keyCallbacks = []
        self.lastKeyPress = (None, None, None)

        super().__init__()

    def connectCallback(self, callback:Callable):
        self.keyCallbacks.append(callback)
    
    def eventFilter(self, qobj:QObject, event:QEvent):
        if event.type() is QEvent.Type.KeyPress \
                and event.text() in self.teamBuzzerInfo.buzzerTeams.keys():
            keyPressInfo = (self.teamBuzzerInfo.buzzerTeams[event.text()], event.text(), event.timestamp())

            if keyPressInfo != self.lastKeyPress:
                logger.debug(f"Handling {keyPressInfo}...")
                self.lastKeyPress = keyPressInfo
                for callback in self.keyCallbacks:
                    callback(keyPressInfo)
            return super(KeyPressHandler, self).eventFilter(qobj, event)
        return False