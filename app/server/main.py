"""
入口

"""
import argparse
import os
import sys
from pathlib import Path
import faulthandler
import threading
import traceback
import logging
import time
from multiprocessing import freeze_support
# Reduce noisy FFmpeg swscaler warnings from OpenCV decode pipeline.
os.environ.setdefault("OPENCV_FFMPEG_LOGLEVEL", "24")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
print(fr"PROJECT_ROOT {PROJECT_ROOT}")
sys.path.append(str(PROJECT_ROOT))


def setup_fatal_handlers(logger):
    log_dir = Path(__file__).resolve().parents[2] / "logs" / "server"
    log_dir.mkdir(parents=True, exist_ok=True)
    fatal_log = log_dir / "fatal.log"
    try:
        fh = open(fatal_log, "a", encoding="utf-8")

        class _TimestampWriter:
            def __init__(self, wrapped):
                self._wrapped = wrapped
                self._line_start = True

            def write(self, data):
                if not data:
                    return 0
                text = str(data)
                total = 0
                for chunk in text.splitlines(True):
                    if self._line_start and chunk.strip():
                        ts = time.strftime("%Y-%m-%d %H:%M:%S ")
                        total += self._wrapped.write(ts)
                    total += self._wrapped.write(chunk)
                    self._line_start = chunk.endswith("\n")
                return total

            def flush(self):
                return self._wrapped.flush()

            def fileno(self):
                return self._wrapped.fileno()

        ts_writer = _TimestampWriter(fh)
        faulthandler.enable(ts_writer)
        faulthandler.dump_traceback_later(120, repeat=True, file=ts_writer)
    except Exception:
        logger.exception("Failed to enable faulthandler")

    def _log_thread_exception(args):
        logger.error(
            "Thread exception: %s",
            "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)).strip(),
        )

    def _log_sys_exception(exc_type, exc_value, exc_traceback):
        logger.error(
            "Unhandled exception: %s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)).strip(),
        )

    threading.excepthook = _log_thread_exception
    sys.excepthook = _log_sys_exception


def _run_capture_loop(camera_manage_config, cool_bed_thread_worker_map, business_main):
    while True:
        steel_infos = {}
        for key, config in camera_manage_config.group_dict.items():
            worker = cool_bed_thread_worker_map[key]
            steel_info = worker.get_steel_info()
            if steel_info is None:
                business_main.mark_fault(f"{key} steel_info timeout", send_fault_signal=True)
                raise TimeoutError(f"{key} steel_info timeout")
            if isinstance(steel_info, dict):
                missing = False
                for group_config in config.groups:
                    if steel_info.get(group_config.group_key) is None and not getattr(group_config, "shield", False):
                        missing = True
                        break
                if missing:
                    business_main.mark_fault(f"{key} steel_info missing", send_fault_signal=True)
                    raise TimeoutError(f"{key} steel_info missing")
            steel_infos[key] = steel_info
        business_main.update(steel_infos)


def _run_http_loop(camera_manage_config, capture_clients, business_main):
    while True:
        steel_infos = {}
        for key, config in camera_manage_config.group_dict.items():
            client = capture_clients.get(key)
            if client is None:
                business_main.mark_fault(f"{key} capture client missing", send_fault_signal=True)
                raise TimeoutError(f"{key} capture client missing")
            steel_info = client.get_steel_info(config)
            if steel_info is None:
                business_main.mark_fault(f"{key} steel_info timeout", send_fault_signal=True)
                raise TimeoutError(f"{key} steel_info timeout")
            if isinstance(steel_info, dict):
                missing = False
                for group_config in config.groups:
                    if steel_info.get(group_config.group_key) is None and not getattr(group_config, "shield", False):
                        missing = True
                        break
                if missing:
                    business_main.mark_fault(f"{key} steel_info missing", send_fault_signal=True)
                    raise TimeoutError(f"{key} steel_info missing")
            steel_infos[key] = steel_info
        business_main.update(steel_infos)


def main(enable_capture: bool):
    if enable_capture:
        os.environ["NG_CAPTURE_AUTO_START"] = "1"
    else:
        os.environ["NG_CAPTURE_AUTO_START"] = "0"

    from Configs.CameraManageConfig import camera_manage_config
    from Configs.CaptureServerConfig import CAPTURE_URLS
    from CaptureClient import CaptureHttpClient
    from Globals import business_main, cool_bed_thread_worker_map, init_cool_bed_workers
    from Loger import logger
    from Server import ApiServer

    # 仅屏蔽 YOLO/ultralytics 的日志，保留其他 FastAPI/uvicorn 等日志
    logging.getLogger("ultralytics").setLevel(logging.ERROR)
    logging.getLogger("yolo").setLevel(logging.ERROR)

    freeze_support()
    setup_fatal_handlers(logger)

    if enable_capture:
        init_cool_bed_workers(enable_capture=True)
    ApiServer.start()

    if enable_capture:
        _run_capture_loop(camera_manage_config, cool_bed_thread_worker_map, business_main)
    else:
        capture_clients = {
            key: CaptureHttpClient(key, CAPTURE_URLS.get(key, ""))
            for key in camera_manage_config.group_dict.keys()
        }
        _run_http_loop(camera_manage_config, capture_clients, business_main)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="store_true", help="enable local camera capture in main process")
    args = parser.parse_args()
    main(enable_capture=args.capture)
