from core.core import Core
from interface.interface import Interface

class Task():
    def __init__(self, _core: Core, _interface: Interface):
        self.core, self.interface = _core, _interface
