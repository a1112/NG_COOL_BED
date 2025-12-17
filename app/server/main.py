"""
入口

"""
import os
import sys
from pathlib import Path
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


def main():
    logger.info("start main")
    while True:
        try:
            steel_infos = {}
            for key, config in camera_manage_config.group_dict.items():
                config: CoolBedGroupConfig  # 冷床 参数中心，用于管理冷床参数
                worker = cool_bed_thread_worker_map[key]
                steel_infos[key] = worker.get_steel_info()
            business_main.update(steel_infos)
        except Exception as e:
            logger.error(fr"主进程存在报错")
            logger.error(e)


if __name__ == "__main__":
    # 仅屏蔽 YOLO/ultralytics 的日志，保留其他 FastAPI/uvicorn 等日志
    logging.getLogger("ultralytics").setLevel(logging.ERROR)
    logging.getLogger("yolo").setLevel(logging.ERROR)

    freeze_support()
    # 启动 HTTP 服务
    ApiServer.start()
    # 启动运行线程
    main()
