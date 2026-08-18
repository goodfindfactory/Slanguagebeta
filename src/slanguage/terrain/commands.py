
from slanguage.terrain.agent import TerrainMapperAgent
from slanguage.terrain.dashboard import render_map


def run_command(agent: TerrainMapperAgent, parts: list[str]) -> dict:
    if not parts:
        return {"status": "EMPTY", "message": ""}

    cmd = parts[0].lower()

    if cmd == "goto":
        if len(parts) < 3:
            return {"status": "ERROR", "message": "Usage: goto <lat> <lon>"}
        lat = float(parts[1])
        lon = float(parts[2])
        agent.set_target(lat, lon)
        status = agent.move_to_target()
        return {
            "status": status,
            "message": "Agent arrived at target." if status == "ARRIVED" else "No target set.",
            "map": render_map(agent),
        }

    if cmd == "step":
        status = agent.step_toward_target()
        return {
            "status": status,
            "message": f"Step status: {status}",
            "map": render_map(agent),
        }

    if cmd == "pos":
        return {"status": "OK", "message": "Position refreshed.", "map": render_map(agent)}

    if cmd in {"help", "?"}:
        return {
            "status": "OK",
            "message": (
                "Commands: goto <lat> <lon> | step | pos | help | exit"
            ),
        }

    if cmd == "exit":
        return {"status": "EXIT", "message": "Terrain mapper closed."}

    return {
        "status": "ERROR",
        "message": "Unknown command. Use: goto, step, pos, help, exit",
    }
