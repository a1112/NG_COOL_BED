import argparse
import sys
import time
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from CameraStreamer.RtspCapTure import RtspCapTure
from Configs.CameraConfig import CameraConfig
from Configs.CameraManageConfig import camera_manage_config
from Configs.GlobalConfig import GlobalConfig


def collect_camera_pairs():
    pairs = []
    seen = set()
    for cool_bed_key, group_config in camera_manage_config.group_dict.items():
        for camera_key in group_config.camera_list:
            key = (cool_bed_key, camera_key)
            if key in seen:
                continue
            seen.add(key)
            pairs.append(key)
    return pairs


def parse_ip_filter(raw):
    if not raw:
        return None
    return {part.strip() for part in str(raw).split(",") if part.strip()}


def main():
    parser = argparse.ArgumentParser(description="Connect all cameras and display with OpenCV.")
    parser.add_argument("--width", type=int, default=400, help="display width")
    parser.add_argument("--height", type=int, default=300, help="display height")
    parser.add_argument("--wait", type=int, default=1, help="cv2.waitKey delay in ms")
    parser.add_argument("--show", action="store_true", help="enable OpenCV windows")
    parser.add_argument("--ip", help="filter by camera ip (comma-separated)")
    args = parser.parse_args()

    global_config = GlobalConfig()
    captures = {}
    ip_filter = parse_ip_filter(args.ip)

    for cool_bed_key, camera_key in collect_camera_pairs():
        camera_config = CameraConfig(cool_bed_key, camera_key)
        if not camera_config.enable:
            print(f"skip disabled camera: {cool_bed_key}/{camera_key}")
            continue
        if ip_filter and camera_config.ip not in ip_filter:
            continue
        capture = RtspCapTure(camera_config, global_config)
        window_name = f"{cool_bed_key}_{camera_key}"
        if args.show:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, args.width, args.height)
        captures[window_name] = capture

    if not captures:
        if ip_filter:
            print(f"no enabled cameras found for ip: {sorted(ip_filter)}")
        else:
            print("no enabled cameras found")
        return

    try:
        while True:
            for window_name, capture in captures.items():
                frame = capture.get_latest_frame()
                if frame is None:
                    continue
                if args.show:
                    resized = cv2.resize(frame, (args.width, args.height))
                    cv2.imshow(window_name, resized)
            if args.show:
                key = cv2.waitKey(args.wait) & 0xFF
                if key in (27, ord("q")):
                    break
            time.sleep(0.01)
    finally:
        for capture in captures.values():
            try:
                capture.camera_config.enable = False
            except Exception:
                pass
        if args.show:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
