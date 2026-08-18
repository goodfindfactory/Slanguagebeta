
from .base_mode import BaseMode

class SpyMode(BaseMode):
    name = "spy"
    tone = "terse"
    description = "Terse, tactical, operator-style."

    def build_context(self, text: str) -> str:
        return f"SPY MODE:\nUser: {text}\nReply tactical."
