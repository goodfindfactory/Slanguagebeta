
from .base_mode import BaseMode

class DivaMode(BaseMode):
    name = "diva"
    tone = "playful"
    description = "Expressive, playful, high-energy."

    def build_context(self, text: str) -> str:
        return f"DIVA MODE:\nUser: {text}\nReply playful."
