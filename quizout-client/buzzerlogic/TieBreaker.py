import logging
import random

from PySide6.QtCore import QObject, QTimer, Signal

from data import TeamBuzzerInfo

logger = logging.getLogger(__name__)

class TieBreaker(QObject):
    playerChosen = Signal(tuple)
    buzzerFrozen = Signal(tuple)

    # Some keyboard buffers treat simultaneous presses as 1ms apart, but always favor the same key. This variable will allow the logic to
    # treat keypresses that are milliseconds apart as simultaneous to try to ensure fairness.
    tieThresholdMS:int = 2
    
    freezeTimeoutLengthMS:int = 500

    listening:bool = False

    def __init__(self, teamBuzzerInfo:TeamBuzzerInfo, tieThresholdMS:int, freezeTimeoutLengthMS:int = 500):
        self.teamBuzzerInfo = teamBuzzerInfo
        self.allTeams = teamBuzzerInfo.teams
        self.chosenTeams = []
        self.afterBuzzTimer = QTimer(singleShot=True)
        self.afterBuzzTimer.timeout.connect(self.onAfterBuzzTimeout)
        self.keypress = None
        self.tieThresholdMS = tieThresholdMS
        self.freezeTimeoutLengthMS = freezeTimeoutLengthMS
        self.randomlyChosenTeam = None
        self.frozenBuzzers = dict()

        super().__init__()

    def startListening(self):
        self.listening = True

    def stopListening(self):
        self.listening = False
        self.resetFrozenBuzzers()

    def fullReset(self):
        self.stopListening()
        self.chosenTeams = []
        self.randomlyChosenTeam = None
        if self.afterBuzzTimer.isActive():
            self.afterBuzzTimer.stop()

    def isListening(self):
        return self.listening

    def handleKeyPress(self, keyPressInfo, inactiveTeams:list = []):
        # If player was frozen previously for buzzing in early, ignore their keypress
        if self.isFrozen(keyPressInfo):
            logger.info(f"Keypress ignored because buzzer '{keyPressInfo[1]}' has been frozen")
            return

        # Player buzzed in early, so freeze the buzzer
        if not self.isListening():
            logger.info(f"Buzzer '{keyPressInfo[1]}' frozen for buzzing in too early")
            self.freezeBuzzer(keyPressInfo)
            return

        # filter out buzzes from inactive teams
        if keyPressInfo[0] in inactiveTeams:
            logger.info(f"Keypress ignored because {keyPressInfo[0]} is one of the inactive teams. ({inactiveTeams})")
            return

        # On the first valid keypress, store the press and start a 500ms timer to capture any other keypresses
        if not self.afterBuzzTimer.isActive():
            self.afterBuzzTimer.setInterval(500)
            self.afterBuzzTimer.start()
            self.keypress = keyPressInfo
            self.randomlyChosenTeam = None
            
        # If another player buzzes in, pick a winner based on timestamps (or random if it's a tie) 
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
                    logger.info(f"TIE! {winningKeypress[0]} chosen by coin toss.")
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
    
    def onAfterBuzzTimeout(self):
        self.stopListening()
        self.playerChosen.emit(self.keypress)

    def freezeBuzzer(self, keyPressInfo):
        (team, key, timestamp) = keyPressInfo
        self.frozenBuzzers[key] = timestamp + self.freezeTimeoutLengthMS
        self.buzzerFrozen.emit((key, self.frozenBuzzers[key]))
        

    def isFrozen(self, keyPressInfo):
        (team, key, timestamp) = keyPressInfo
        return key in self.frozenBuzzers.keys() and timestamp <= self.frozenBuzzers[key]


    def resetFrozenBuzzers(self):
        self.frozenBuzzers = dict()