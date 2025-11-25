"""
Batch perspective-warp the calibration assets into mapping/{sub-folder}.

Usage examples (run from repo root or double-click with Python file association):

    python config/camera/calibrate/auto_perspective.py
    python config/camera/calibrate/auto_perspective.py --subfolder calibrate
    python config/camera/calibrate/auto_perspective.py --dry-run

The script scans each direct child folder under the calibration directory,
looks for *.json + image pairs, applies a perspective transform using the
LabelMe "Area" polygon, and writes the warped images into the matching
mapping/{folder} directory. Existing XML annotations in mapping/ are kept.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np


CALIBRATE_ROOT = Path(__file__).parent
MAPPING_ROOT = CALIBRATE_ROOT.parent / "mapping"
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply perspective transform for each calibration folder into mapping/{folder}."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=CALIBRATE_ROOT,
        help="Calibration root directory (defaults to config/camera/calibrate).",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=MAPPING_ROOT,
        help="Mapping root directory (defaults to config/camera/mapping).",
    )
    parser.add_argument(
        "--subfolder",
        type=str,
        help="Only process the named subfolder under the calibration root.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without writing warped images.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove previously generated images in each mapping/{folder} before writing (XML files are preserved).",
    )
    return parser.parse_args()


def list_source_folders(root: Path, single: Optional[str]) -> List[Path]:
    if single:
        folder = root / single
        if not folder.is_dir():
            raise FileNotFoundError(f"Source folder does not exist: {folder}")
        return [folder]
    return [child for child in root.iterdir() if child.is_dir()]


def candidate_image(json_path: Path) -> Optional[Path]:
    base = json_path.with_suffix("")
    for suffix in IMAGE_SUFFIXES:
        candidate = base.with_suffix(suffix)
        if candidate.exists():
            return candidate
    return None


def load_area_points(json_path: Path) -> np.ndarray:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    shapes = data.get("shapes", [])
    for shape in shapes:
        if shape.get("label", "").lower() == "area":
            points = shape.get("points")
            if isinstance(points, Sequence) and len(points) == 4:
                return order_points(points, json_path.stem)
    raise ValueError(f"{json_path} missing Area shape with 4 points")


def order_points(points: Sequence[Sequence[float]], key: str) -> np.ndarray:
    pts = np.array(points, dtype=np.float32)
    if pts.shape != (4, 2):
        raise ValueError("points must be 4x2")

    # Default ordering via sum/diff heuristic.
    ordered = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    ordered[0] = pts[np.argmin(s)]  # top-left
    ordered[2] = pts[np.argmax(s)]  # bottom-right
    ordered[1] = pts[np.argmin(diff)]  # top-right
    ordered[3] = pts[np.argmax(diff)]  # bottom-left

    # Special-case overrides can be added here if needed per key.
    return ordered


def compute_destination_size(pts: np.ndarray) -> Tuple[int, int]:
    (tl, tr, br, bl) = pts
    width_top = np.linalg.norm(tr - tl)
    width_bottom = np.linalg.norm(br - bl)
    height_left = np.linalg.norm(bl - tl)
    height_right = np.linalg.norm(br - tr)

    max_width = max(width_top, width_bottom)
    max_height = max(height_left, height_right)
    return max(1, int(round(max_width))), max(1, int(round(max_height)))


def warp_image(image_path: Path, pts: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    img = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to read image: {image_path}")
    width, height = size
    dst = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img, matrix, (width, height))
    return warped


def clean_generated_images(folder: Path) -> None:
    if not folder.exists():
        return
    for path in folder.iterdir():
        if path.is_file() and path.suffix.lower() != ".xml":
            path.unlink()


def process_folder(src_folder: Path, dst_folder: Path, dry_run: bool) -> Tuple[int, int]:
    total = updated = 0
    dst_folder.mkdir(parents=True, exist_ok=True)

    for json_path in src_folder.glob("*.json"):
        image_path = candidate_image(json_path)
        if image_path is None:
            print(f"[skip] {json_path}: matching image not found")
            continue

        total += 1
        dest_file = dst_folder / image_path.name

        try:
            pts = load_area_points(json_path)
            size = compute_destination_size(pts)
        except ValueError as exc:
            print(f"[skip] {json_path}: {exc}")
            continue

        if dry_run:
            print(f"[dry-run] would warp {image_path} -> {dest_file} ({size[0]}x{size[1]})")
            updated += 1
            continue

        warped = warp_image(image_path, pts, size)
        ok, buffer = cv2.imencode(image_path.suffix, warped)
        if not ok:
            print(f"[error] Failed to encode {dest_file}")
            continue
        dest_file.write_bytes(buffer.tobytes())
        print(f"[ok] {image_path} -> {dest_file}")
        updated += 1

    return total, updated


def main() -> None:
    args = parse_args()
    source_root = args.source.resolve()
    target_root = args.target.resolve()

    if not source_root.is_dir():
        raise SystemExit(f"Source root does not exist: {source_root}")
    target_root.mkdir(parents=True, exist_ok=True)

    folders = list_source_folders(source_root, args.subfolder)
    if not folders:
        print("No folders to process.")
        return

    for folder in folders:
        relative_name = folder.name
        destination = target_root / relative_name
        print(f"\n=== {relative_name} ===")
        if args.clean and not args.dry_run:
            clean_generated_images(destination)
            print(f"Cleared old generated images in {destination} (XML preserved).")
        total, updated = process_folder(folder, destination, args.dry_run)
        action = "would warp" if args.dry_run else "warped"
        print(f"{relative_name}: {updated}/{total} file(s) {action}.")


if __name__ == "__main__":
    main()
