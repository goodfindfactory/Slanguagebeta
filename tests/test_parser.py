import unittest

from slanguage.bootstrap import build
from slanguage.core.parser import SlanguageParser


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = SlanguageParser()

    def test_structured_command(self):
        cmd = self.parser.parse("Spy scan 37.7 -122.4")
        self.assertTrue(cmd.valid)
        self.assertEqual(cmd.mode, "spy")
        self.assertEqual(cmd.intent, "scan")
        self.assertEqual(cmd.payload, "37.7 -122.4")

    def test_casual_prompt_is_not_structured(self):
        cmd = self.parser.parse("spy status")
        self.assertFalse(cmd.valid)


class RuntimeParserIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.rt = build()

    def test_casual_prompt_still_uses_modes(self):
        out = self.rt.handle("spy status", entity="slanguage")
        self.assertIn("[terse]", out)

    def test_vault_intent_uses_enforcer(self):
        out = self.rt.handle("ponder vault", entity="slanguage")
        self.assertIn("vault entity=slanguage", out)
        self.assertIn("PetAI_Core", out)

    def test_scan_intent_uses_terrain(self):
        out = self.rt.handle("spy scan 40.0 -100.0", entity="slanguage")
        self.assertIn("scan ARRIVED", out)

    def test_guest_structured_command_is_locked(self):
        from slanguage.vault.vault_enforcer import OmniLockTriggered

        with self.assertRaises(OmniLockTriggered):
            self.rt.handle("diva vault", entity="guest")


if __name__ == "__main__":
    unittest.main()
