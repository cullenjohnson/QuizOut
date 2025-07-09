import logging
import random

from PySide6.QtCore import QObject, QTimer, Signal

from quizSession.QuizSessionConfig import QuizSessionConfig

logger = logging.getLogger(__name__)

# TODO add logic for second place?
class TieBreaker(QObject):

    playerChosen = Signal(tuple)

    def __init__(self, quizSessionConfig:QuizSessionConfig):
        self.quizSessionConfig = quizSessionConfig
        self.allTeams = quizSessionConfig.teams
        self.chosenTeams = []
        self.timer = QTimer(singleShot=True)
        self.timer.timeout.connect(self.onTimeout)
        self.keypress = None

        super().__init__()

    def activate(self, keyPressInfo):
        if not self.timer.isActive():
            self.timer.setInterval(500)
            self.timer.start()
            self.keypress = None
        
        if self.keypress is None:
            self.keypress = keyPressInfo
        else:
            self.keypress = self.pickAWinner(keyPressInfo, self.keypress)

    def pickAWinner(self, keypress1, keypress2):
        (team1, key1, timestamp1) = keypress1
        (team2, key2, timestamp2) = keypress2

        # Pick fastest buzz
        if timestamp1 < timestamp2:
            return keypress1

        elif timestamp2 < timestamp1:
            return keypress2

        else:
            # If there's a tie between players on the same team, pick random
            if team1 == team2:
                return random.choice([keypress1, keypress2])

            # Handle ties: Pick the team that was least recently randomly picked or pick random if not applicable
            else:
                # Reset the list of chosen teams if every team has been chosen randomly
                if len(self.chosenTeams) == len(self.allTeams):
                    self.chosenTeams = []

                winningKeypress = None

                index1 = -1
                if team1 in self.chosenTeams:
                    index1 = self.chosenTeams.index(team1)
                index2 = -1
                if team2 in self.chosenTeams:
                    index2 = self.chosenTeams.index(team2)
                
                # Neither team has been chosen before
                if index1 == index2:
                    winningKeypress = random.choice([keypress1, keypress2])
                    logger.info("TIE! Player chosen at random.")
                # team for keypress1 was chosen least recently
                elif index1 < index2:
                    winningKeypress = keypress1
                    logger.info(f"TIE! {team1} chosen because {team2} was randomly chosen more recently.")
                # team for keypress2 was chosen least recently
                else:
                    winningKeypress = keypress2
                    logger.info(f"TIE! {team2} chosen because {team1} was randomly chosen more recently.")
                
                self.chosenTeams.append(winningKeypress[0])
                return winningKeypress
    
    def onTimeout(self):
        self.playerChosen.emit(self.keypress)