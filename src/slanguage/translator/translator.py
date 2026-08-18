
import json
from pathlib import Path

class SlanguageTranslator:
    def __init__(self, base_path: Path):
        self.slang_map = self._load(base_path / "slang_map.json")
        self.mode_map = self._load(base_path / "mode_map.json")
        self.sigil_map = self._load(base_path / "sigil_map.json")
        self.vault_map = self._load(base_path / "vault_map.json")

    def _load(self, path: Path):
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def translate(self, text: str):
        tokens = text.lower().split()
        mode = self._detect_mode(tokens)
        sigils = self._detect_sigils(tokens)
        vault = self._detect_vault(tokens)
        cleaned = self._clean_text(tokens)
        return {
            "mode": mode,
            "sigils": sigils,
            "vault": vault,
            "cleaned_text": cleaned
        }

    def _detect_mode(self, tokens):
        for t in tokens:
            if t in self.mode_map:
                return self.mode_map[t]
        return None

    def _detect_sigils(self, tokens):
        found = []
        for t in tokens:
            if t in self.sigil_map:
                found.append(self.sigil_map[t])
        return found

    def _detect_vault(self, tokens):
        found = []
        for t in tokens:
            if t in self.vault_map:
                found.append(self.vault_map[t])
        return found

    def _clean_text(self, tokens):
        filtered = [
            t for t in tokens
            if t not in self.slang_map
            and t not in self.mode_map
            and t not in self.sigil_map
            and t not in self.vault_map
        ]
        return " ".join(filtered)
