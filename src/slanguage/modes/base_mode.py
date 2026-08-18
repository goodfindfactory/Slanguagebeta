
class BaseMode:
    name = "base"
    description = "Base passthrough mode."
    tone = None

    def __init__(self, runtime):
        self.runtime = runtime

    def build_context(self, text: str) -> str:
        return text

    def postprocess(self, out: str) -> str:
        if self.tone:
            return f"[{self.tone}] {out}"
        return out
