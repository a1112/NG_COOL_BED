"""
Utility to null out the `imageData` field in LabelMe-style JSON files.

Run from anywhere, optionally pointing at a specific directory or file:

    python del_imageData.py                           # default: this folder
    python del_imageData.py ..\\..\\some\\folder      # custom folder
    python del_imageData.py path\\to\\file.json       # single file

Use --dry-run to preview which files would be touched.
"""

import argparse
import json
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set imageData=null for every JSON file under the target path."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=Path(__file__).parent,
        type=Path,
        help="Folder or JSON file to process (defaults to this script's directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report files that would change without touching them.",
    )
    return parser.parse_args()


def iter_json_files(target: Path) -> Iterable[Path]:
    if target.is_file():
        if target.suffix.lower() == ".json":
            yield target
        return

    for path in target.rglob("*.json"):
        if path.is_file():
            yield path


def null_out_image_data(path: Path, dry_run: bool) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[skip] {path}: {exc}")
        return False

    if not isinstance(data, dict):
        print(f"[skip] {path}: JSON root is not an object")
        return False

    if data.get("imageData") is None:
        return False

    data["imageData"] = None
    if dry_run:
        return True

    serialized = json.dumps(data, ensure_ascii=True, indent=2)
    path.write_text(serialized + "\n", encoding="utf-8")
    return True


def main() -> None:
    args = parse_args()
    target = args.target.resolve()

    if not target.exists():
        raise SystemExit(f"Target path does not exist: {target}")

    total = changed = 0
    for json_file in iter_json_files(target):
        total += 1
        updated = null_out_image_data(json_file, args.dry_run)
        if updated:
            changed += 1
            action = "would update" if args.dry_run else "updated"
            print(f"[{action}] {json_file}")

    summary_action = "would be updated" if args.dry_run else "updated"
    print(f"{changed}/{total} file(s) {summary_action}.")


if __name__ == "__main__":
    main()
