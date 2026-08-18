
from pathlib import Path

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

        if parsed["mode"]:
            self.set_mode(parsed["mode"])

        if parsed["vault"]:
            construct = parsed["vault"][0]

        self.vault.check_access(entity, construct)

        mode = self.modes.active
        if mode is None:
            raise RuntimeError("No active mode registered. Call register_mode() first.")

        ctx = mode.build_context(parsed["cleaned_text"])
        out = self.llm.generate(ctx)
        return mode.postprocess(out)
