import unittest

from slanguage.bootstrap import EchoLLM, build
from slanguage.core.runtime import SlanguageRuntime
from slanguage.modes.diva_mode import DivaMode
from slanguage.modes.ponder_mode import PonderMode
from slanguage.modes.spy_mode import SpyMode
from slanguage.vault.vault_enforcer import (
    OmniLockTriggered,
    VaultCategoryEnforcer,
    VaultCategoryError,
)


class VaultEnforcerTests(unittest.TestCase):
    def setUp(self):
        self.vault = VaultCategoryEnforcer(operator_name="slanguage")
        self.vault.bind_construct("PetAI_Core", ["Agent Templates"])
        self.vault.bind_construct("World2_Shards", ["World Shards"])
        self.vault.bind_construct("NPC_Core", ["NPCs"])

    def test_operator_bypasses_all_checks(self):
        self.assertTrue(
            self.vault.check_access("slanguage", "PetAI_Core")
        )

    def test_non_operator_without_category_is_omni_locked(self):
        with self.assertRaises(OmniLockTriggered):
            self.vault.check_access("guest_npc", "PetAI_Core")

    def test_non_operator_with_matching_category_is_allowed(self):
        self.vault.grant_category("guest_npc", "Agent Templates")
        self.assertTrue(
            self.vault.check_access("guest_npc", "PetAI_Core")
        )

    def test_non_operator_with_wrong_category_is_omni_locked(self):
        self.vault.grant_category("guest_npc", "World Shards")
        with self.assertRaises(OmniLockTriggered):
            self.vault.check_access("guest_npc", "PetAI_Core")

    def test_unknown_construct_raises(self):
        with self.assertRaises(VaultCategoryError):
            self.vault.check_access("guest_npc", "Missing_Construct")

    def test_get_granted_and_required(self):
        self.vault.grant_category("scout", "NPCs")
        self.assertEqual(self.vault.get_granted("scout"), {"NPCs"})
        self.assertEqual(
            self.vault.get_required("NPC_Core"),
            {"NPCs"},
        )


class RuntimeAccessTests(unittest.TestCase):
    def setUp(self):
        self.rt = SlanguageRuntime(llm_client=EchoLLM(), operator="slanguage")
        self.rt.register_mode(DivaMode)
        self.rt.register_mode(SpyMode)
        self.rt.register_mode(PonderMode)
        self.rt.set_mode("diva")

    def test_operator_handle_succeeds(self):
        out = self.rt.handle("hello", entity="slanguage", construct="PetAI_Core")
        self.assertIn("[LLM OUTPUT]", out)

    def test_guest_without_grant_is_blocked(self):
        with self.assertRaises(OmniLockTriggered):
            self.rt.handle("hello", entity="guest", construct="PetAI_Core")

    def test_guest_with_grant_succeeds(self):
        self.rt.vault.grant_category("guest", "Agent Templates")
        out = self.rt.handle("hello", entity="guest", construct="PetAI_Core")
        self.assertIn("[LLM OUTPUT]", out)

    def test_guest_blocked_on_world_shard_without_grant(self):
        with self.assertRaises(OmniLockTriggered):
            self.rt.handle("hello", entity="guest", construct="World2_Shards")

    def test_guest_world_access_after_category_grant(self):
        self.rt.vault.grant_category("guest", "World Shards")
        out = self.rt.handle("hello", entity="guest", construct="World2_Shards")
        self.assertIn("[LLM OUTPUT]", out)

    def test_vault_token_switches_construct_for_guest(self):
        self.rt.vault.grant_category("npc_timmy", "NPCs")
        out = self.rt.handle(
            "npc status check",
            entity="npc_timmy",
            construct="PetAI_Core",
        )
        self.assertIn("[LLM OUTPUT]", out)

    def test_vault_token_denied_when_guest_lacks_npc_category(self):
        with self.assertRaises(OmniLockTriggered):
            self.rt.handle(
                "npc status check",
                entity="npc_timmy",
                construct="PetAI_Core",
            )


class BuiltRuntimeAccessTests(unittest.TestCase):
    def test_demo_guest_entity_blocked_until_granted(self):
        rt = build()
        with self.assertRaises(OmniLockTriggered):
            rt.handle("ponder hello", entity="demo_guest")

        rt.vault.grant_category("demo_guest", "Agent Templates")
        out = rt.handle("ponder hello", entity="demo_guest")
        self.assertIn("[reflective]", out)


if __name__ == "__main__":
    unittest.main()
