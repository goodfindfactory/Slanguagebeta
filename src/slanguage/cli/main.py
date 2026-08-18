
from slanguage.bootstrap import DEFAULT_CONSTRUCT, DEFAULT_ENTITY, build, handle_prompt

EXIT_COMMANDS = {"exit", "quit", "q"}


def print_help():
    print(
        "Commands: exit | quit | help\n"
        "Slanguage tokens: diva, spy, ponder (switch mode)\n"
        "Vault tokens: agent-template, world2, npc\n"
        "Sigils: lock-sigil, vault-sigil"
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="SlanguageOS CLI")
    parser.add_argument("--mode", default="diva")
    parser.add_argument("--entity", default=DEFAULT_ENTITY)
    parser.add_argument("--construct", default=DEFAULT_CONSTRUCT)
    parser.add_argument(
        "--once",
        metavar="TEXT",
        help="Process one prompt and exit (non-interactive demo)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the tkinter GUI",
    )
    parser.add_argument(
        "--terrain",
        action="store_true",
        help="Launch the terrain mapper CLI",
    )
    args = parser.parse_args()

    if args.terrain:
        from slanguage.terrain.cli import main as terrain_main

        terrain_main()
        return

    if args.gui:
        from slanguage.gui.app import launch_gui

        launch_gui()
        return

    rt = build()
    rt.set_mode(args.mode)

    if args.once is not None:
        print(
            handle_prompt(
                rt,
                args.once,
                entity=args.entity,
                construct=args.construct,
            )
        )
        return

    print(f"SlanguageOS running in {args.mode} mode. Type 'help' or 'exit' to quit.")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not text:
            continue

        if text.lower() in EXIT_COMMANDS:
            break

        if text.lower() == "help":
            print_help()
            continue

        print(
            handle_prompt(
                rt,
                text,
                entity=args.entity,
                construct=args.construct,
            )
        )


if __name__ == "__main__":
    main()
