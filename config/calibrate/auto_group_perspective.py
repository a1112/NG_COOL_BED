"""
根据各标定子目录的数据，按分组生成透视后的拼接图片，例如：
    L1_g0_2345.jpg、L1_g1_6.jpg、L1_g2_1.jpg、L2_g0_2345.jpg 等。

特点：
- 使用 src 目录下与线上一致的透视逻辑（ConversionImage）；
- 每个分组按各标定子目录里的 CameraManage.json 的 camera_list 和 size_list 做透视并横向拼接；
- 默认对 cameras 下所有标定子目录批量生成，输出到 mapping/{子目录}/{group}.jpg；
- 可用 --subfolder 仅处理指定的标定子目录；不修改 / 删除其中的 XML 文件。

用法（在仓库根或 config/calibrate 目录运行）：
    python config/calibrate/auto_group_perspective.py             # 处理 cameras 下所有标定子目录
    python config/calibrate/auto_group_perspective.py --subfolder calibrate1124
    python config/calibrate/auto_group_perspective.py --key L1_g0_2345 --subfolder calibrate
    python config/calibrate/auto_group_perspective.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from CameraStreamer.ConversionImage import ConversionImage  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="按分组生成透视拼接图到 mapping/{标定子目录}（不修改 XML）。"
    )
    parser.add_argument(
        "--key",
        type=str,
        help="只生成指定分组，如 L1_g0_2345；默认全部分组。",
    )
    parser.add_argument(
        "--subfolder",
        type=str,
        help="仅处理 cameras 下指定标定子目录，例如：calibrate1124。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将要生成的文件，不实际写入。",
    )
    return parser.parse_args()


def load_group_defs(camera_manage_path: Path):
    data = json.loads(camera_manage_path.read_text(encoding="utf-8"))
    groups = {}
    for cool_bed_key, cfg in data.get("group", {}).items():
        for g in cfg.get("group", []):
            key = g["key"]
            groups[key] = g
    return groups


def load_image(path: Path) -> np.ndarray:
    buf = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to read image: {path}")
    return img


def build_group_image(group_key: str, group_cfg: dict, calibrate_root: Path) -> np.ndarray:
    camera_list = group_cfg["camera_list"]
    size_list = group_cfg["size_list"]
    assert len(camera_list) == len(size_list), f"{group_key}: camera_list 与 size_list 数量不一致"

    warped_list = []
    for cam_key, (w, h) in zip(camera_list, size_list):
        src_img_path = calibrate_root / f"{cam_key}.jpg"
        if not src_img_path.is_file():
            raise FileNotFoundError(f"{group_key}: 找不到源图像 {src_img_path}")

        img = load_image(src_img_path)
        conv = ConversionImage(cam_key, w, h, calibrate_root)
        warped = conv.image_conversion(img)
        warped_list.append(warped)

    if not warped_list:
        raise ValueError(f"{group_key}: 没有可用的相机图像")

    if len(warped_list) == 1:
        return warped_list[0]
    return np.hstack(warped_list)


def save_image(path: Path, img: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, buf = cv2.imencode(path.suffix or ".jpg", img)
    if not ok:
        raise ValueError(f"Failed to encode image: {path}")
    path.write_bytes(buf.tobytes())


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).parent
    cameras_root = base_dir / "cameras"
    mapping_root = base_dir / "mapping"

    if not cameras_root.is_dir():
        print(f"标定目录不存在: {cameras_root}")
        return

    target_folders = []
    if args.subfolder:
        target = cameras_root / args.subfolder
        if target.is_dir():
            target_folders = [target]
        else:
            print(f"指定子目录不存在: {target}")
            return
    else:
        target_folders = [p for p in cameras_root.iterdir() if p.is_dir() and (p / "CameraManage.json").is_file()]

    if not target_folders:
        print("没有找到任何包含 CameraManage.json 的标定子目录。")
        return

    for calib_folder in target_folders:
        camera_manage_path = calib_folder / "CameraManage.json"
        if not camera_manage_path.is_file():
            print(f"[skip] {calib_folder.name}: 缺少 CameraManage.json")
            continue

        groups = load_group_defs(camera_manage_path)
        if args.key:
            groups = {k: v for k, v in groups.items() if k == args.key}
        if not groups:
            print(f"[skip] {calib_folder.name}: 无分组匹配 {args.key or '全部'}")
            continue

        out_root = mapping_root / calib_folder.name
        out_root.mkdir(parents=True, exist_ok=True)

        for key, cfg in groups.items():
            out_path = out_root / f"{key}.jpg"
            print(f"[group] {calib_folder.name}:{key} -> {out_path}")

            if args.dry_run:
                continue

            try:
                img = build_group_image(key, cfg, calib_folder)
            except Exception as exc:  # noqa: BLE001
                print(f"[skip] {calib_folder.name}:{key}: {exc}")
                continue

            save_image(out_path, img)
            print(f"[ok] saved {out_path}")


if __name__ == "__main__":
    main()
