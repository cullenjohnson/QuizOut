import logging
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QKeyEvent

logger = logging.getLogger(__name__)

class KeyPressHandler(QObject):
    
    def eventFilter(self, qobj:QObject, event:QEvent):
        if isinstance(event, QKeyEvent):
            logger.info("KeyPress!")
            return super(KeyPressHandler, self).eventFilter(qobj, event)
        return False