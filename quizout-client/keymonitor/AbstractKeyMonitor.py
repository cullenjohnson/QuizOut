from abc import ABC, abstractmethod
from .GlobalKeyMonitorCommunicator import GlobalKeyMonitorCommunicator

class AbstractKeyMonitor(ABC):
    @property
    @abstractmethod
    def _communicator(self) -> GlobalKeyMonitorCommunicator:
        pass

    @abstractmethod
    def monitor_keyboards(self):
        pass