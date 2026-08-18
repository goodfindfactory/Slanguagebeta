
from slanguage.terrain.agent import TerrainMapperAgent
from slanguage.terrain.biomes import biome_at


def render_map(agent: TerrainMapperAgent, width: int = 41, height: int = 21) -> str:
    ax = agent.x
    ay = agent.y
    tx = agent.target_x
    ty = agent.target_y

    half_w = width // 2
    half_h = height // 2

    lines = [
        "SlanguageOS Terrain Mapper",
        "",
        f"Agent (grid): [{ax:.2f}, {ay:.2f}]",
        f"Target (grid): [{tx}, {ty}]",
        f"Earth target (lat/lon): [{agent.target_lat}, {agent.target_lon}]",
        "",
        "Legend: @ agent  T target  ~ ocean  w lake  \" wetland",
        "        , grass  # forest  % jungle  . desert  * tundra  ^ mountains",
        "",
    ]

    for row in range(-half_h, half_h + 1):
        cells = []
        gx = int(round(ax))
        gy = int(round(ay))
        txg = int(round(tx)) if tx is not None else None
        tyg = int(round(ty)) if ty is not None else None

        for col in range(-half_w, half_w + 1):
            if col == gx and row == gy:
                cells.append("@")
            elif txg is not None and col == txg and row == tyg:
                cells.append("T")
            else:
                cell_lat = (row + ay) / agent.scale
                cell_lon = (col + ax) / agent.scale
                cells.append(biome_at(cell_lat, cell_lon))
        lines.append("".join(cells))

    return "\n".join(lines)


def reset_cursor() -> None:
    print("\033[H", end="")


def clear_screen_once() -> None:
    print("\033[2J", end="")


def draw_dashboard(agent: TerrainMapperAgent, width: int = 41, height: int = 21) -> None:
    reset_cursor()
    print(render_map(agent, width=width, height=height))
    print("\nEnter next command below:")
