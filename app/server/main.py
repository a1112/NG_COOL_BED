"""
入口

"""
import os
import sys
from pathlib import Path
import faulthandler
import threading
import traceback
print(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))
from multiprocessing import freeze_support
import logging

# Reduce noisy FFmpeg swscaler warnings from OpenCV decode pipeline.
os.environ.setdefault("OPENCV_FFMPEG_LOGLEVEL", "24")

from Configs.CameraManageConfig import camera_manage_config
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Globals import cool_bed_thread_worker_map, business_main
from Loger import logger
from Server import ApiServer



def setup_fatal_handlers():
    log_dir = Path(__file__).resolve().parents[2] / "logs" / "server"
    log_dir.mkdir(parents=True, exist_ok=True)
    fatal_log = log_dir / "fatal.log"
    try:
        fh = open(fatal_log, "a", encoding="utf-8")
        faulthandler.enable(fh)
        faulthandler.dump_traceback_later(120, repeat=True, file=fh)
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

def main():
    logger.info("start main")
    while True:
        try:
            steel_infos = {}
            for key, config in camera_manage_config.group_dict.items():
                config: CoolBedGroupConfig  # ?????? ???????????????????????????????????????
                worker = cool_bed_thread_worker_map[key]
                steel_info = worker.get_steel_info(timeout=1.0)
                if steel_info is None:
                    business_main.mark_fault(f"{key} steel_info timeout", send_fault_signal=True)
                    raise TimeoutError(f"{key} steel_info timeout")
                if isinstance(steel_info, dict):
                    missing = False
                    for group_config in config.groups:
                        if steel_info.get(group_config.group_key) is None and not getattr(group_config, 'shield', False):
                            missing = True
                            break
                    if missing:
                        business_main.mark_fault(f"{key} steel_info missing", send_fault_signal=True)
                        raise TimeoutError(f"{key} steel_info missing")
                steel_infos[key] = steel_info
            business_main.update(steel_infos)
        except Exception as e:
            logger.error(fr"主进程存在报错")
            logger.error(e)
            try:
                business_main.mark_fault(e, send_fault_signal=True)
            except Exception:
                pass


if __name__ == "__main__":
    # 仅屏蔽 YOLO/ultralytics 的日志，保留其他 FastAPI/uvicorn 等日志
    logging.getLogger("ultralytics").setLevel(logging.ERROR)
    logging.getLogger("yolo").setLevel(logging.ERROR)

    freeze_support()
    setup_fatal_handlers()
    # 启动 HTTP 服务
    ApiServer.start()
    # 启动运行线程
    main()
