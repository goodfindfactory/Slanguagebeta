
from .base_mode import BaseMode

class PonderMode(BaseMode):
    name = "ponder"
    tone = "reflective"
    description = "Slow, reflective reasoning."

    def build_context(self, text: str) -> str:
        return f"PONDER MODE:\nUser: {text}\nReply stepwise."
