import logging
from collections.abc import Callable
import time

from data import TeamBuzzerInfo

logger = logging.getLogger(__name__)

class KeyPressHandler:

    def __init__(self, teamBuzzerInfo: TeamBuzzerInfo):
        self.teamBuzzerInfo = teamBuzzerInfo
        self.keyCallbacks = []
        self.lastKeyPress = (None, None, None)

    def connectCallback(self, callback: Callable):
        self.keyCallbacks.append(callback)
    
    def handle_key_press(self, key_char: str):
        """Handle a key press from any source"""
        if key_char in self.teamBuzzerInfo.buzzerTeams.keys():
            timestamp = int(time.time() * 1000)
            keyPressInfo = (self.teamBuzzerInfo.buzzerTeams[key_char], key_char, timestamp)
            
            if keyPressInfo != self.lastKeyPress:
                logger.debug(f"Handling {keyPressInfo}...")
                self.lastKeyPress = keyPressInfo
                for callback in self.keyCallbacks:
                    callback(keyPressInfo)