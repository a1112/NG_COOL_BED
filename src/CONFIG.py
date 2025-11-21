import socket
from enum import Enum
from pathlib import Path

from threading import Thread
from multiprocessing import Process

import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# CONFIG
CONFIG_FOLDER = Path(__file__).parent.parent/"config"
if not CONFIG_FOLDER.is_dir():
    CONFIG_FOLDER = Path("D:/NG_CONFIG")


assert CONFIG_FOLDER.exists(), f"CONFIG_FOLDER 不存在： {CONFIG_FOLDER}"

SOFT_FOLDER = ""
for folder in [CONFIG_FOLDER / "soft", CONFIG_FOLDER.parent / "soft", Path(__file__).parent.parent/"soft"]:
    if folder.exists():
        SOFT_FOLDER = folder
        break

FIRST_SAVE_FOLDER = CONFIG_FOLDER / "first_save"


CAMERA_CONFIG_FOLDER = CONFIG_FOLDER / "camera"


IP_LIST_CAMERA_CONFIG = CONFIG_FOLDER / "camera"/"IpList.json"
CAMERA_MANAGE_CONFIG = CONFIG_FOLDER / "camera"/"CameraManage.json"

CalibratePath = CAMERA_CONFIG_FOLDER/"calibrate"/"calibrate"
MappingPath = CAMERA_CONFIG_FOLDER/"mapping"


SAVE_CONFIG = CONFIG_FOLDER / "camera"/"Save.json"

MODEL_FOLDER = CONFIG_FOLDER / "model"

lOG_DIR = CONFIG_FOLDER / "log"
lOG_DIR.mkdir(exist_ok=True, parents=True)
encoding = "utf-8"

MappingPath.mkdir(exist_ok=True, parents=True)
FIRST_SAVE_FOLDER.mkdir(exist_ok=True, parents=True)
DATA_FOLDER = CONFIG_FOLDER / "data"
DATA_FOLDER.mkdir(exist_ok=True, parents=True)
DEBUG_MODEL = False
print(f"hostname: {socket.gethostname()}")
if socket.gethostname() in ["DESKTOP-3VCH6DO", "MS-LGKRSZGOVODD", "DESKTOP-94ADH1G","HGL8081-1"]:
    DEBUG_MODEL = True

show_camera = False

CapTureBaseClass = Thread

class CapModelEnum(Enum):
    OPENCV=1
    AV=2
    SDK=3
    DEBUG=4

CAP_MODEL = CapModelEnum.SDK
CAMERA_SAVE_FOLDER = Path(fr"D:\NgDataSave")

TEMP_FOLDER = CAMERA_SAVE_FOLDER/"temp"

if DEBUG_MODEL:
    CAP_MODEL = CapModelEnum.DEBUG
    CAMERA_SAVE_FOLDER = CONFIG_FOLDER / "data"

CAMERA_SAVE_FOLDER.mkdir(exist_ok=True, parents=True)
TEMP_FOLDER.mkdir(exist_ok=True, parents=True)

DATA_FMT="%Y-%m-%d"
TIME_FMT="%H_%M_%S"

DATETIME_FMT = f"{DATA_FMT}-{TIME_FMT}"
IMAGE_SAVE_TYPE = "jpg"
APP_RUN = True


class DebugControl:
    def __init__(self):
        self.debug_test_index=0

    def next(self):
        print(fr"next:{self.debug_test_index}")
        self.debug_test_index+=1
        return self.debug_test_index

    def prev(self):
        print(fr"prev:{self.debug_test_index}")
        self.debug_test_index-=1
        return self.debug_test_index

useSegModel=False

debug_control = DebugControl()
