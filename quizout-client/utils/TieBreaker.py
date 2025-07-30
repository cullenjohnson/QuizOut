import logging
import random

from PySide6.QtCore import QObject, QTimer, Signal

from data import TeamBuzzerInfo

logger = logging.getLogger(__name__)

class TieBreaker(QObject):

    playerChosen = Signal(tuple)
    # Some keyboard buffers treat simultaneous presses as 1ms apart, but always favor the same key. This variable will allow the logic to
    # treat keypresses that are milliseconds apart as simultaneous to try to ensure fairness.
    tieThresholdMS:int = 2

    def __init__(self, teamBuzzerInfo:TeamBuzzerInfo, tieThresholdMS:int):
        self.teamBuzzerInfo = teamBuzzerInfo
        self.allTeams = teamBuzzerInfo.teams
        self.chosenTeams = []
        self.timer = QTimer(singleShot=True)
        self.timer.timeout.connect(self.onTimeout)
        self.keypress = None
        self.tieThresholdMS = tieThresholdMS

        super().__init__()

    def activate(self, keyPressInfo, inactiveTeams:list = []):
        # filter out buzzes from inactive teams
        if keyPressInfo[0] in inactiveTeams:
            logger.info(f"Keypress ignored because {keyPressInfo[0]} is one of the inactive teams. ({inactiveTeams})")
            return

        if not self.timer.isActive():
            self.timer.setInterval(500)
            self.timer.start()
            self.keypress = None
            self.randomlyChosenTeam = None
        
        if self.keypress is None:
            self.keypress = keyPressInfo
        else:
            self.keypress = self.pickAWinner(keyPressInfo, self.keypress)

    def pickAWinner(self, keypress1, keypress2):
        (team1, key1, timestamp1) = keypress1
        (team2, key2, timestamp2) = keypress2

        timeDifference = timestamp1 - timestamp2

        # Pick fastest buzz
        if abs(timeDifference) > self.tieThresholdMS:
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

                # If one of the teams was chosen as the result of a previous tie-break within the same tiebreaker timer session, stay with that choice.
                if team1 == self.randomlyChosenTeam:
                    logger.info(f"TIE! {team1} chosen because they were already randomly chosen in the current tiebreaker session.")
                    return keypress1
                elif team2 == self.randomlyChosenTeam:
                    logger.info(f"TIE! {team2} chosen because they were already randomly chosen in the current tiebreaker session.")
                    return keypress2

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
                    logger.info("TIE! {winnindKeypress[0]} chosen by coin toss.")
                # team for keypress1 was chosen least recently
                elif index1 < index2:
                    winningKeypress = keypress1
                    logger.info(f"TIE! {team1} chosen because {team2} was randomly chosen more recently.")
                # team for keypress2 was chosen least recently
                else:
                    winningKeypress = keypress2
                    logger.info(f"TIE! {team2} chosen because {team1} was randomly chosen more recently.")
                
                self.chosenTeams.append(winningKeypress[0])
                self.randomlyChosenTeam = winningKeypress[0]
                return winningKeypress
    
    def onTimeout(self):
        self.playerChosen.emit(self.keypress)