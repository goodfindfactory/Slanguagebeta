
class ModeRegistry:
    def __init__(self):
        self._modes = {}
        self.active = None

    def add(self, mode):
        self._modes[mode.name] = mode
        if self.active is None:
            self.active = mode

    def activate(self, name: str):
        if name not in self._modes:
            raise ValueError(f"Unknown mode: {name}")
        self.active = self._modes[name]
