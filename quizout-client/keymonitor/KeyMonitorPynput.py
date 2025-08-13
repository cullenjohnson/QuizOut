import logging
from pynput import keyboard

from .AbstractKeyMonitor import AbstractKeyMonitor
from .GlobalKeyMonitorCommunicator import GlobalKeyMonitorCommunicator

logger = logging.getLogger(__name__)

class KeyMonitorPynput(AbstractKeyMonitor):

    _communicator: GlobalKeyMonitorCommunicator
    _pressedKeys:list[str]

    def __init__(self, communicator):
        self._communicator = communicator
        self._pressedKeys = []

    def communicator(self) -> GlobalKeyMonitorCommunicator:
        return self._communicator

    def monitor_keyboards(self):
        self.listener = keyboard.Listener(on_press = self._on_key_press, on_release = self._on_key_release)
        self.listener.start()

    def _on_key_press(self, key):
        try:
            # Only handle character keys
            if hasattr(key, 'char') and key.char is not None and key.char not in self._pressedKeys:
                # This list ensures players can't hold down a button for multiple rapid keypresses
                self._pressedKeys.append(key.char)
                key_char = key.char
            else:
                # Special keys are ignored
                return
            
            self._communicator.keypress.emit(key_char)

        except Exception as e:
            logger.error(f"Error handling global key press: {e}")

    def _on_key_release(self, key):
        try:
            # Convert pynput key to character if possible
            if hasattr(key, 'char') and key.char in self._pressedKeys:
                self._pressedKeys.remove(key.char)
            else:
                # Special keys are ignored
                return

        except Exception as e:
            logger.error(f"Error handling global key release: {e}")