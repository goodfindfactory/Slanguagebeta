
import importlib
from pathlib import Path

SKIP_MODULES = {"loader", "__init__"}


def load_modules(base_path: Path):
    modules_dir = base_path / "modules"
    loaded = []
    for py in sorted(modules_dir.glob("*.py")):
        name = py.stem
        if name in SKIP_MODULES:
            continue
        mod = importlib.import_module(f"slanguage.modules.{name}")
        loaded.append(mod)
    return loaded
