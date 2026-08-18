import unittest

from slanguage.bootstrap import build
from slanguage.terrain import TerrainMapperAgent, render_map, run_command
from slanguage.terrain.biomes import biome_at, water_at


class BiomeTests(unittest.TestCase):
    def test_water_is_deterministic(self):
        self.assertEqual(water_at(10.0, 20.0), water_at(10.0, 20.0))

    def test_biome_is_deterministic(self):
        self.assertEqual(biome_at(45.0, -120.0), biome_at(45.0, -120.0))


class AgentTests(unittest.TestCase):
    def test_goto_and_arrive(self):
        agent = TerrainMapperAgent()
        agent.set_target(37.7749, -122.4194)
        status = agent.move_to_target()
        self.assertEqual(status, "ARRIVED")
        self.assertAlmostEqual(agent.x, agent.target_x, places=2)
        self.assertAlmostEqual(agent.y, agent.target_y, places=2)

    def test_render_map_shows_agent(self):
        agent = TerrainMapperAgent()
        text = render_map(agent)
        self.assertIn("@", text)
        self.assertIn("SlanguageOS Terrain Mapper", text)


class CommandTests(unittest.TestCase):
    def test_goto_command(self):
        agent = TerrainMapperAgent()
        result = run_command(agent, ["goto", "40.0", "-100.0"])
        self.assertEqual(result["status"], "ARRIVED")
        self.assertIn("map", result)

    def test_pos_command(self):
        agent = TerrainMapperAgent()
        result = run_command(agent, ["pos"])
        self.assertEqual(result["status"], "OK")
        self.assertIn("@", result["map"])


class RuntimeIntegrationTests(unittest.TestCase):
    def test_build_attaches_terrain_mapper(self):
        rt = build()
        self.assertTrue(hasattr(rt, "terrain"))
        self.assertIsInstance(rt.terrain, TerrainMapperAgent)


if __name__ == "__main__":
    unittest.main()
