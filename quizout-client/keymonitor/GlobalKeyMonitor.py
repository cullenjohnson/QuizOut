import logging
import time
import platform
from PySide6.QtCore import QObject
from collections.abc import Callable

if platform.system() == "Windows":
    EVDEV_AVAILABLE = False
    from keymonitor.KeyMonitorPynput import KeyMonitorPynput
else:
    import evdev
    from keymonitor.KeyMonitorEvDev import KeyMonitorEvDev
    EVDEV_AVAILABLE = True

from data import TeamBuzzerInfo
from .GlobalKeyMonitorCommunicator import GlobalKeyMonitorCommunicator
from .AbstractKeyMonitor import AbstractKeyMonitor

logger = logging.getLogger(__name__)

class GlobalKeyMonitor(QObject):
    _communicator: GlobalKeyMonitorCommunicator
    _keyMonitor: AbstractKeyMonitor
    _keyCallbacks: list[Callable]

    def __init__(self, teamBuzzerInfoConfig:TeamBuzzerInfo):
        self.teamBuzzerInfo = teamBuzzerInfoConfig
        self.lastKeyPress = (None, None, None)
        self._keyCallbacks = []
        self._communicator = GlobalKeyMonitorCommunicator()
        self._communicator.keypress.connect(self._handle_key_press)

        if EVDEV_AVAILABLE:
            self._keyMonitor = KeyMonitorEvDev(self._communicator)
        else:
            self._keyMonitor = KeyMonitorPynput(self._communicator)
    
    def start_monitoring(self):
        self._keyMonitor.monitor_keyboards()

    def register_callback(self, callback: Callable):
        self._keyCallbacks.append(callback)

    def _handle_key_press(self, key_char: str):
        """Handle a key press from any source"""
        if key_char in self.teamBuzzerInfo.buzzerTeams.keys():
            timestamp = int(time.time() * 1000)
            keyPressInfo = (self.teamBuzzerInfo.buzzerTeams[key_char], key_char, timestamp)
            
            if keyPressInfo != self.lastKeyPress:
                logger.debug(f"Handling {keyPressInfo}...")
                self.lastKeyPress = keyPressInfo
                for callback in self._keyCallbacks:
                    callback(keyPressInfo)
            
            
    
    