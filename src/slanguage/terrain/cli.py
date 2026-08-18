
import time

from slanguage.terrain.agent import TerrainMapperAgent
from slanguage.terrain.commands import run_command
from slanguage.terrain.dashboard import clear_screen_once, draw_dashboard, render_map


def main() -> None:
    agent = TerrainMapperAgent()
    clear_screen_once()
    print("SlanguageOS Terrain Mapper started.")
    print("Commands: goto <lat> <lon> | step | pos | help | exit\n")

    while True:
        try:
            raw = input("terrain> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        parts = raw.split()
        if not parts:
            continue

        if parts[0].lower() == "goto" and len(parts) >= 3:
            lat = float(parts[1])
            lon = float(parts[2])
            agent.set_target(lat, lon)
            while True:
                status = agent.step_toward_target()
                draw_dashboard(agent)
                time.sleep(0.05)
                if status == "ARRIVED":
                    draw_dashboard(agent)
                    print("\nAgent has arrived at target.")
                    break
            continue

        result = run_command(agent, parts)
        if result.get("map"):
            print(result["map"])
        if result.get("message"):
            print(result["message"])
        if result.get("status") == "EXIT":
            break


if __name__ == "__main__":
    main()
