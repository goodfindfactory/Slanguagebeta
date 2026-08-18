
from slanguage.terrain.agent import TerrainMapperAgent


def install(runtime):
    runtime.terrain = TerrainMapperAgent()
