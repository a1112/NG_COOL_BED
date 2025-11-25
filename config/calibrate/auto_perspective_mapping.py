"""
在 config/calibrate 下运行本脚本，可以根据 cameras 里的各子文件夹，
自动做透视变换并生成到 mapping/{子文件夹}/camera/{相机名}.jpg 中。

- 只写入图片文件，不修改 / 删除 mapping 中已有的 XML 标注；
- 只删除旧图片可用 --clean（XML 保留不动）；
- 可用 --subfolder 只处理某个子目录，例如：calibrate1124。

示例：
    python auto_perspective_mapping.py                          # 处理 cameras 下所有子目录
    python auto_perspective_mapping.py --subfolder calibrate    # 结果在 mapping/calibrate/camera/L1_1.jpg
    python auto_perspective_mapping.py --subfolder calibrate1124
    python auto_perspective_mapping.py --dry-run
"""

import argparse
import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).parent
CALIBRATE_DIR = BASE_DIR / "cameras"
MAPPING_DIR = BASE_DIR / "mapping"
AUTO_PERSPECTIVE_PATH = CALIBRATE_DIR / "auto_perspective.py"


def load_auto_module():
    spec = importlib.util.spec_from_file_location(
        "camera_calib_auto_perspective", AUTO_PERSPECTIVE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从 cameras 各子文件夹生成透视后的图片到 mapping/{子文件夹}/camera（不修改 XML）。"
    )
    parser.add_argument(
        "--subfolder",
        type=str,
        help="只处理 cameras 下指定子目录（例如：calibrate、calibrate1124）。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示将要处理的文件，不实际写入。",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="处理前清理 mapping 对应子目录下除 XML 以外的旧文件（XML 保留）。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    module = load_auto_module()

    source_root = CALIBRATE_DIR
    target_root = MAPPING_DIR

    if not source_root.is_dir():
        raise SystemExit(f"Source cameras root does not exist: {source_root}")
    target_root.mkdir(parents=True, exist_ok=True)

    folders = module.list_source_folders(source_root, args.subfolder)
    if not folders:
        print("No folders to process.")
        return

    for folder in folders:
        relative_name = folder.name
        destination = target_root / relative_name / "camera"
        print(f"\n=== {relative_name} ===")

        if args.clean and not args.dry_run:
            module.clean_generated_images(destination)
            print(f"Cleared old generated images in {destination} (XML preserved).")

        total, updated = module.process_folder(folder, destination, args.dry_run)
        action = "would warp" if args.dry_run else "warped"
        print(f"{relative_name}: {updated}/{total} file(s) {action}.")


if __name__ == "__main__":
    main()
