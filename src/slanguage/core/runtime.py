from pathlib import Path

from slanguage.core.parser import SlanguageParser
from slanguage.core.registry import ModeRegistry
from slanguage.translator.translator import SlanguageTranslator
from slanguage.vault.vault_enforcer import VaultCategoryEnforcer


class SlanguageRuntime:
    def __init__(self, llm_client, operator="slanguage", vault=None):
        self.llm = llm_client
        self.operator = operator
        self.modes = ModeRegistry()
        self.vault = vault or VaultCategoryEnforcer(operator_name=operator)
        self.translator = SlanguageTranslator(Path(__file__).parent.parent / "translator")
        self.parser = SlanguageParser()

        self._bootstrap_vault()

    def _bootstrap_vault(self):
        self.vault.grant_category(self.operator, "Agent Templates")
        self.vault.grant_category(self.operator, "World Shards")
        self.vault.grant_category(self.operator, "NPCs")
        self.vault.bind_construct("PetAI_Core", ["Agent Templates"])
        self.vault.bind_construct("World2_Shards", ["World Shards"])
        self.vault.bind_construct("NPC_Core", ["NPCs"])

    def register_mode(self, mode_cls):
        mode = mode_cls(runtime=self)
        self.modes.add(mode)
        return mode

    def set_mode(self, name: str):
        self.modes.activate(name)

    def handle(self, text: str, entity=None, construct="PetAI_Core") -> str:
        entity = entity or self.operator
        parsed = self.translator.translate(text)
        command = self.parser.parse(text)

        if parsed["mode"]:
            self.set_mode(parsed["mode"])
        elif command.mode and command.mode != "slanguage":
            self.set_mode(command.mode)

        if parsed["vault"]:
            construct = parsed["vault"][0]

        self.vault.check_access(entity, construct)

        if command.valid and command.intent:
            routed = self._route_intent(command, entity=entity, construct=construct)
            if routed is not None:
                mode = self.modes.active
                return mode.postprocess(routed) if mode else routed

        mode = self.modes.active
        if mode is None:
            raise RuntimeError("No active mode registered. Call register_mode() first.")

        ctx = mode.build_context(parsed["cleaned_text"])
        out = self.llm.generate(ctx)
        return mode.postprocess(out)

    def _route_intent(self, command, *, entity: str, construct: str) -> str | None:
        intent = command.intent
        payload = command.payload

        if intent == "vault":
            granted = sorted(self.vault.get_granted(entity))
            constructs = sorted(self.vault.construct_requirements.keys())
            return (
                f"vault entity={entity} construct={construct} "
                f"granted={granted or ['(none)']} constructs={constructs}"
            )

        if intent == "scan":
            terrain = getattr(self, "terrain", None)
            if terrain is None:
                return f"scan: {payload or 'no terrain mapper attached'}"
            from slanguage.terrain.commands import run_command

            if payload:
                parts = payload.split()
                if len(parts) >= 2:
                    result = run_command(terrain, ["goto", parts[0], parts[1]])
                    return f"scan {result['status']}: {result['message']}"
            result = run_command(terrain, ["pos"])
            return f"scan {result['status']}: {result['message']}"

        if intent == "shift" and payload.lower() in {"diva", "spy", "ponder"}:
            self.set_mode(payload.lower())
            return f"shifted to {payload.lower()}"

        if intent == "shabbykevkev":
            self.vault.grant_category(entity, "Agent Templates")
            return f"vault save acknowledged for {entity}"

        if intent == "shabbysowwystay":
            if entity != self.operator:
                return f"master key denied for {entity}"
            return "master key acknowledged"

        if intent in {"build", "summon", "drop"}:
            mode = self.modes.active
            if mode is None:
                return f"{intent}: {payload}"
            ctx = mode.build_context(f"{intent} {payload}".strip())
            return self.llm.generate(ctx)

        return None
