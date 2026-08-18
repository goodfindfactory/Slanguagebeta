
# SlanguageOS

Mode-based conversational runtime with:
- Diva / Spy / Ponder modes
- Vault category enforcement
- Slanguage translator
- Third-party module loader
- Terrain mapper with biomes and Earth coordinates
- Tkinter GUI with vault access testing

All entry points share one bootstrap: `slanguage.bootstrap.build()`.

## Unified entry points

| Command | Purpose |
|---|---|
| `python3 run.py` | Interactive CLI |
| `python3 run.py --gui` | GUI |
| `python3 run_gui.py` | GUI launcher |
| `python3 run_terrain.py` | Terrain mapper CLI |
| `python3 run.py --terrain` | Terrain mapper via main launcher |
| `python3 run.py --once "text"` | One-shot prompt |
| `python3 examples/demo.py` | Smoke demo |
| `python3 run_tests.py` | Vault access tests |
| `python3 verify.py` | Verify all entry points |
| `python3 -m slanguage.cli.main` | Module CLI |
| `slanguage` / `slanguage-gui` / `slanguage-terrain` | Installed scripts (after `pip3 install -e .`) |

## Quick start

```bash
cd SlanguageOS

python3 verify.py
python3 run.py
python3 run_gui.py
```

## Install

```bash
pip3 install -e .
slanguage --once "hello"
slanguage-gui
```

## Vault access tests

```bash
python3 run_tests.py
```

Example CLI checks:

```bash
python3 run.py --once "hello" --entity slanguage
python3 run.py --once "hello" --entity guest
```

Guest access without grants returns `[OMNI-LOCK]` consistently across CLI and GUI.

## Terrain mapper

Earth-coordinate terrain navigation with ASCII biomes and water tiles.

```bash
python3 run_terrain.py
python3 run.py --terrain
slanguage-terrain
```

Commands: `goto <lat> <lon>` | `step` | `pos` | `help` | `exit`

The GUI includes a Terrain Mapper panel with lat/lon goto, step, and live map refresh.
The runtime exposes `runtime.terrain` after bootstrap via `terrain_module`.

## Slanguage tokens

| Token | Effect |
|---|---|
| `diva`, `spy`, `ponder` | Switch mode |
| `agent-template`, `world2`, `npc` | Vault construct routing |
| `shabboost`, `shabsoft` | Slang modifiers (stripped from prompt) |

## Modules

Drop Python files into `src/slanguage/modules/`. Each module can define `install(runtime)` to hook into the OS.
