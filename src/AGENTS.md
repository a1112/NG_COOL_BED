# Repository Guidelines

## Project Structure & Module Organization
- `main.py` is the entry point that wires camera groups, PLC workers, and the HTTP API.
- `Configs/` holds per-line and camera configuration objects; update these instead of hard-coding constants.
- `Base/`, `alg/`, `Detector/`, and `CameraStreamer/` contain processing pipelines; `Server/` exposes REST handlers.
- `Loger/` wraps project-wide logging; `scripts/` hosts utility jobs; `test/` contains PLC integration checks.
- Shared singletons such as thread workers live in `Globals.py`; reuse them rather than instantiating duplicates.

## Build, Test, and Development Commands
- `python -m venv .venv` then `.venv\Scripts\Activate.ps1` to isolate dependencies.
- `python main.py` starts the PLC sync loop and API server; use in a lab network.
- `python -m compileall Base Detector` quickly checks for syntax errors before committing.
- `python scripts\clip_image.py --input Result\ --output Save\clips` trims captured frames for offline analysis.

## Coding Style & Naming Conventions
- Follow 4-space indentation, `snake_case` for variables/functions, and `PascalCase` for classes (see `CoolBedGroupConfig`).
- Prefer explicit imports from project packages; avoid wildcard imports to keep PLC dependencies obvious.
- Use `Loger.logger` for runtime diagnostics; emit structured messages such as `logger.info("start main")`.
- Keep configuration in `CONFIG.py`/`Configs/*`; gate environment-specific constants behind descriptive names.

## Testing Guidelines
- Hardware-facing checks live in `test/plc_test*.py`; run them with `python test\plc_test.py` only when the target PLC is reachable.
- Add pure Python unit tests under `test/unit_*.py` (create directory if needed) and name them after the module under test.
- Mock PLC I/O by patching `SiemensS7Net` when adding new logic; capture expected payloads in `Result/`.
- Record observed latency or temperature ranges in test assertions to guard against regressions.

## Commit & Pull Request Guidelines
- Recent history uses short lowercase summaries (example: `add`, `ch`); keep titles under 50 characters and focus on the outcome.
- Group related PLC or camera changes per commit; include config edits alongside the code that consumes them.
- PRs must list operator-impact, test evidence (`python main.py --dry-run` output or screenshots), and any configuration files touched.
- Link Jira or issue IDs in the PR body and mention safety checks (network isolation, hardware mock status).

## Configuration & Operations Notes
- Document IP changes in `PLC_config.py` and `Configs/CoolBedGroupConfig.py`, then notify operations before deployment.
- Store runtime artifacts under `Result/` and move long-term archives to `Save/`; avoid committing raw PLC dumps.
- When introducing new cameras, extend `Configs/CameraManageConfig.py` and register workers in `Globals.cool_bed_thread_worker_map`.
