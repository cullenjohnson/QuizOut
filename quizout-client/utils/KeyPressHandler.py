import logging
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QKeyEvent, Qt
from quizSession import QuizSessionConfig

logger = logging.getLogger(__name__)

class KeyPressHandler(QObject):

    def __init__(self, quizSessionConfig:QuizSessionConfig):
        self.quizSessionConfig = quizSessionConfig

        super().__init__()

    
    def eventFilter(self, qobj:QObject, event:QEvent):
        if event.type() is QEvent.Type.KeyPress and event.text() in self.quizSessionConfig.buzzerTeams.keys():
            logger.info("KeyPress!")
            return super(KeyPressHandler, self).eventFilter(qobj, event)
        return False