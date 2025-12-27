from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import CONFIG
from alg.YoloModel import SteelAreaSegModel, SteelDetModel


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Continuous YOLO test using current models")
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "seg",
        help="Directory with sample images",
    )
    parser.add_argument(
        "--mode",
        choices=["seg", "det", "both"],
        default="det",
        help="Which model(s) to run",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Batch size for segmentation model",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of images used (0 for all)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        help="Sleep seconds between loops",
    )
    parser.add_argument(
        "--log-interval",
        type=float,
        default=5.0,
        help="Log progress every N seconds (0 to disable)",
    )
    return parser.parse_args()


def load_image(path: Path) -> Image.Image:
    with Image.open(path) as img:
        return img.copy()


def collect_images(image_dir: Path, limit: int) -> list[Path]:
    if not image_dir.exists():
        raise FileNotFoundError(f"image_dir not found: {image_dir}")

    images = [p for p in sorted(image_dir.iterdir()) if p.suffix.lower() in IMAGE_EXTENSIONS]
    if limit > 0:
        images = images[:limit]
    if not images:
        raise FileNotFoundError(f"no images found in: {image_dir}")
    return images


def run_seg(model: SteelAreaSegModel, images: list[Image.Image], batch_size: int) -> int:
    count = 0
    batch = []
    for image in images:
        batch.append(image)
        if len(batch) >= batch_size:
            model.predict(batch)
            count += len(batch)
            batch = []
    if batch:
        model.predict(batch)
        count += len(batch)
    return count


def run_det(model: SteelDetModel, images: list[Image.Image]) -> int:
    count = 0
    for image in images:
        model.get_steel_rect(image)
        count += 1
    return count


def main() -> int:
    args = parse_args()
    image_paths = collect_images(args.image_dir, args.limit)
    images = [load_image(p) for p in image_paths]

    print(f"model_folder={CONFIG.MODEL_FOLDER}")
    print(f"device={CONFIG.YOLO_DEVICE}")
    print(f"images={len(images)} mode={args.mode}")

    seg_model = SteelAreaSegModel() if args.mode in ("seg", "both") else None
    det_model = SteelDetModel() if args.mode in ("det", "both") else None

    start = time.perf_counter()
    last_log = start
    seg_count = 0
    det_count = 0

    try:
        while True:
            if seg_model is not None:
                seg_count += run_seg(seg_model, images, max(1, args.batch_size))
            if det_model is not None:
                det_count += run_det(det_model, images)

            now = time.perf_counter()
            if args.log_interval > 0 and now - last_log >= args.log_interval:
                elapsed = now - start
                total = seg_count + det_count
                fps = total / elapsed if elapsed > 0 else 0.0
                print(
                    f"elapsed_s={elapsed:.1f} seg={seg_count} det={det_count} total={total} fps={fps:.2f}"
                )
                last_log = now

            if args.sleep > 0:
                time.sleep(args.sleep)
    except KeyboardInterrupt:
        print("stopped")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
