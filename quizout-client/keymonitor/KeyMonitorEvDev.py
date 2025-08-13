import logging
import threading
import select
import evdev

from .AbstractKeyMonitor import AbstractKeyMonitor
from .GlobalKeyMonitorCommunicator import GlobalKeyMonitorCommunicator

logger = logging.getLogger(__name__)

class KeyMonitorEvDev(AbstractKeyMonitor):

    _communicator: GlobalKeyMonitorCommunicator

    def __init__(self, communicator: GlobalKeyMonitorCommunicator):
        self._communicator = communicator

    def _communicator(self) -> GlobalKeyMonitorCommunicator:
        return self._commmunicator

    def monitor_keyboards(self):
        # Start monitoring in daemon thread
        thread = threading.Thread(target=self._listen_for_keypresses, daemon=True)
        thread.start()

    def _listen_for_keypresses(self):
        logger = logging.getLogger(__name__)
        devices = []
        
        try:
            for path in evdev.list_devices():
                device = evdev.InputDevice(path)
                caps = device.capabilities()
                # Check if it's a keyboard
                if evdev.ecodes.EV_KEY in caps and evdev.ecodes.KEY_A in caps.get(evdev.ecodes.EV_KEY, []):
                    devices.append(device)
                    logger.info(f'Monitoring keyboard: {device.name}')
            
            if not devices:
                logger.warning('No keyboards found for global monitoring')
                return
            
            logger.info('Global keyboard monitoring started')
            while True:
                r, w, x = select.select(devices, [], [], 0.1)
                for device in r:
                    for event in device.read():
                        if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # Key press
                            try:
                                # Try to convert keycode to character
                                if event.code >= evdev.ecodes.KEY_1 and event.code <= evdev.ecodes.KEY_9:
                                    char = str(event.code - evdev.ecodes.KEY_1 + 1)
                                    self._communicator.keypress.emit(char)
                                elif event.code == evdev.ecodes.KEY_0:
                                    self._communicator.keypress.emit('0')
                                elif event.code >= evdev.ecodes.KEY_A and event.code <= evdev.ecodes.KEY_Z:
                                    char = chr(event.code - evdev.ecodes.KEY_A + ord('a'))
                                    self._communicator.keypress.emit(char)
                            except Exception as e:
                                logger.debug(f"Error processing key event: {e}")
        except Exception as e:
            logger.error(f"Global keyboard monitoring error: {e}")