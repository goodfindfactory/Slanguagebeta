from dataclasses import dataclass


MODES = {"slanguage", "diva", "spy", "ponder"}
INTENTS = {
    "build",
    "scan",
    "vault",
    "summon",
    "drop",
    "shift",
    "shabbykevkev",
    "shabbysowwystay",
}
MODIFIERS = {"softly", "aggressive", "operator-style", "emergent", "truth-mode"}


@dataclass
class SlanguageCommand:
    raw: str
    mode: str | None
    intent: str | None
    payload: str
    modifiers: list[str]
    valid: bool
    errors: list[str]


class SlanguageParser:
    """Parse structured `mode intent [modifiers] payload` commands."""

    def tokenize(self, text: str) -> list[str]:
        return text.strip().split()

    def parse(self, text: str) -> SlanguageCommand:
        tokens = self.tokenize(text)
        errors: list[str] = []

        mode = None
        intent = None
        modifiers: list[str] = []
        payload_tokens: list[str] = []

        if tokens and tokens[0].lower() in MODES:
            mode = tokens.pop(0).lower()
        else:
            errors.append("Invalid or missing mode token")

        if tokens and tokens[0].lower() in INTENTS:
            intent = tokens.pop(0).lower()
        else:
            errors.append("Invalid or missing intent token")

        for token in tokens:
            lowered = token.lower()
            if lowered in MODIFIERS:
                modifiers.append(lowered)
            else:
                payload_tokens.append(token)

        return SlanguageCommand(
            raw=text,
            mode=mode,
            intent=intent,
            payload=" ".join(payload_tokens),
            modifiers=modifiers,
            valid=len(errors) == 0,
            errors=errors,
        )
