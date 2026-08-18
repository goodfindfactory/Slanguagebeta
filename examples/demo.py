#!/usr/bin/env python3
"""Non-interactive smoke demo for SlanguageOS."""

from slanguage.bootstrap import DEFAULT_ENTITY, MODES, build, handle_prompt


def main():
    rt = build()
    prompts = [
        ("diva", "hello there"),
        ("spy", "status report"),
        ("ponder", "what is consciousness"),
        ("diva", "diva shabboost agent-template mission brief"),
    ]

    print("SlanguageOS smoke demo\n" + "=" * 40)
    for mode, text in prompts:
        rt.set_mode(mode)
        out = handle_prompt(rt, text, entity=DEFAULT_ENTITY)
        print(f"\nmode={mode}  input={text!r}")
        print(out)


if __name__ == "__main__":
    main()
