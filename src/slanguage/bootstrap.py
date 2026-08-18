import json
from pathlib import Path

from slanguage.core.runtime import SlanguageRuntime
from slanguage.modes.diva_mode import DivaMode
from slanguage.modes.ponder_mode import PonderMode
from slanguage.modes.spy_mode import SpyMode
from slanguage.modules.loader import load_modules
from slanguage.vault.vault_enforcer import OmniLockTriggered, VaultCategoryError

ROOT = Path(__file__).resolve().parent

MODES = ["diva", "spy", "ponder"]
PRESET_ENTITIES = ["slanguage", "guest", "npc_timmy", "world_agent"]
DEFAULT_MODE = "diva"
DEFAULT_ENTITY = "slanguage"
DEFAULT_CONSTRUCT = "PetAI_Core"


class EchoLLM:
    def generate(self, prompt: str) -> str:
        return f"[LLM OUTPUT] {prompt}"


def load_vault_manifest() -> dict:
    path = ROOT / "vault" / "vault_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_categories() -> list[str]:
    return load_vault_manifest()["categories"]


def build(verbose: bool = False) -> SlanguageRuntime:
    rt = SlanguageRuntime(llm_client=EchoLLM(), operator=DEFAULT_ENTITY)
    rt.verbose = verbose

    for mode_cls in (DivaMode, SpyMode, PonderMode):
        rt.register_mode(mode_cls)

    for mod in load_modules(ROOT):
        if hasattr(mod, "install"):
            mod.install(rt)

    return rt


def get_constructs(rt: SlanguageRuntime) -> list[str]:
    return sorted(rt.vault.construct_requirements.keys())


def handle_prompt(
    rt: SlanguageRuntime,
    text: str,
    *,
    entity: str | None = None,
    construct: str | None = None,
) -> str:
    try:
        return rt.handle(
            text,
            entity=entity or DEFAULT_ENTITY,
            construct=construct or DEFAULT_CONSTRUCT,
        )
    except (OmniLockTriggered, VaultCategoryError) as exc:
        return f"[OMNI-LOCK] {exc}"
    except Exception as exc:
        return f"[ERROR] {exc}"
