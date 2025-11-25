# Repository Guidelines

## Project Structure & Module Organization
- `app/server/`: Python services for camera capture, YOLO inference, PLC comms, and APIs (`main.py` entry); configurations live in `app/server/Configs/`.
- `app/UI/NG_COOL_BED_UI/`: Qt 6 Quick + QML desktop UI (CMake project with `main.cpp`, QML under `qml/`, assets in `icons/`).
- `config/`: Camera calibration, mapping data, and pretrained weights (`config/model/steel*.pt`); treat files here as source of truth.
- `ultralytics/`: Vendored YOLO codebase; prefer extending via server-side wrappers before modifying core libs.
- `train/`, `script/`, `test/`: Data prep utilities, ad-hoc experiments, and sample tests/images; `doc/` holds interface and IP references; `save_data/` and `work/` store collected or design artifacts.

## Build, Test, and Development Commands
- Install Python deps: `python -m pip install -r requirements.txt` (use the torch index in `README.md` if GPU builds are needed).
- Run backend loop + HTTP server: `python app/server/main.py`.
- UI build (Qt 6 installed): `cmake -S app/UI/NG_COOL_BED_UI -B build/ui -DCMAKE_PREFIX_PATH="C:/Qt/6.x/msvc*/lib/cmake"` then `cmake --build build/ui --config Release`.
- Quick checks: `python test/undistortTest.py` for calibration math, or `python -m pytest test` for any pytest-style suites.

## Coding Style & Naming Conventions
- Follow PEP 8 (see `README.md`) with 4-space indents; .editorconfig formats JSON/YAML splitting arrays/objects across lines.
- Python: `snake_case` for modules/functions, `PascalCase` for classes, constants upper-case; prefer type hints in `app/server/*` logic and keep logging via the shared `Loger` utilities.
- QML/C++: component names in `PascalCase`, QML ids in `camelCase`; keep resource paths relative to qrc.
- Config files: avoid renaming keys in calibration/mapping JSON unless coordinated, as they drive runtime loading.

## Testing Guidelines
- Place new tests in `test/` with `test_*.py` names; prefer pytest assertions over print-based checks.
- Limit GPU/model-heavy runs to small samples before full jobs; reuse fixtures in `test/seg/` images to validate segmentation paths.
- When adjusting `ultralytics/` logic, add minimal regression cases that exercise model loading and a single inference call.

## Commit & Pull Request Guidelines
- Recent history favors short, descriptive messages (often Chinese); keep them concise: e.g., `重构: 相机配置解析` or `修复: PLC 连接超时`.
- PRs should state purpose, scope, and risk, link an issue/task, and note any configs/models touched; include UI screenshots for QML changes and mention test commands executed.

## Security & Configuration Tips
- Do not commit real VPN/credential updates; scrub secrets from `config/calibrate/*.json` and server configs before sharing.
- Back up calibration/mapping files and model weights (`config/model/*.pt`) before experimentation; large binaries should stay out of review unless essential.
