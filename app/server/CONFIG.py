import socket
from enum import Enum
from pathlib import Path
import json

from threading import Thread
from multiprocessing import Process

import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# CONFIG
# 项目根目录：app/server/CONFIG.py 向上两级即仓库根
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 支持多种配置位置：优先使用 D:/NG_CONFIG，其次仓库内的 config
_CONFIG_CANDIDATES = [
    Path("D:/NG_CONFIG"),
    PROJECT_ROOT / "config",
]
CONFIG_FOLDER = next((p for p in _CONFIG_CANDIDATES if p.is_dir()), None)
if CONFIG_FOLDER is None:
    raise FileNotFoundError(f"CONFIG_FOLDER 不存在，已尝试: {', '.join(str(p) for p in _CONFIG_CANDIDATES)}")

IS_LOC = CONFIG_FOLDER.resolve() == (PROJECT_ROOT / "config").resolve()

SOFT_FOLDER = next(
    (p for p in [
        CONFIG_FOLDER / "soft",
        CONFIG_FOLDER.parent / "soft",
        PROJECT_ROOT / "soft",
    ] if p.exists()),
    None,
)

FIRST_SAVE_FOLDER = CONFIG_FOLDER / "first_save"

SAVE_DATA_FOLDER = PROJECT_ROOT / "save_data"
SAVE_DATA_FOLDER.mkdir(exist_ok=True, parents=True)

ONE_CAP_FOLDER = SAVE_DATA_FOLDER / "one_cap"
ONE_CAP_FOLDER.mkdir(exist_ok=True, parents=True)

# 配置根目录已由 camera 重命名为 calibrate
CAMERA_CONFIG_FOLDER = CONFIG_FOLDER / "calibrate"


IP_LIST_CAMERA_CONFIG = CAMERA_CONFIG_FOLDER / "IpList.json"
# calibrate.json 现在位于 config/calibrate/calibrate.json，用于指定 current
CALIBRATE_SELECT_FILE = CAMERA_CONFIG_FOLDER / "calibrate.json"
# UI / API 自定义设置文件（不覆盖基础配置）
SETTINGS_CONFIG_FILE = CAMERA_CONFIG_FOLDER / "settings.json"


def _load_current_calibrate() -> str:
    """
    读取 calibrate/calibrate.json 中的 current 字段，决定使用哪个标定子目录。
    若文件缺失或解析失败，回退到 'calibrate'。
    """
    try:
        data = json.loads(CALIBRATE_SELECT_FILE.read_text(encoding="utf-8"))
        current = data.get("current")
        if isinstance(current, str) and current.strip():
            return current.strip()
    except Exception:
        pass
    return "calibrate"


CURRENT_CALIBRATE = _load_current_calibrate()

# 当前使用的标定透视数据目录与 CameraManage.json 均从 current 指定的子目录读取
CALIBRATE_ROOT = CAMERA_CONFIG_FOLDER / "cameras" / CURRENT_CALIBRATE
CAMERA_MANAGE_CONFIG = CALIBRATE_ROOT / "CameraManage.json"
CalibratePath = CALIBRATE_ROOT
MappingPath = CAMERA_CONFIG_FOLDER / "mapping"
# 当前标定对应的映射目录（用于运行时读取/写入分组图）
MappingCurrent = MappingPath / CURRENT_CALIBRATE


SAVE_CONFIG = CAMERA_CONFIG_FOLDER / "Save.json"

MODEL_FOLDER = CONFIG_FOLDER / "model"
YOLO_DEVICE = "cuda:0"

lOG_DIR = CONFIG_FOLDER / "log"
lOG_DIR.mkdir(exist_ok=True, parents=True)
encoding = "utf-8"

MappingPath.mkdir(exist_ok=True, parents=True)
MappingCurrent.mkdir(exist_ok=True, parents=True)
if not IS_LOC:
    FIRST_SAVE_FOLDER.mkdir(exist_ok=True, parents=True)
DATA_FOLDER = CONFIG_FOLDER / "data"
DATA_FOLDER.mkdir(exist_ok=True, parents=True)
DEBUG_MODEL = False
print(f"hostname: {socket.gethostname()}")
if socket.gethostname() in ["DESKTOP-3VCH6DO", "MS-LGKRSZGOVODD", "DESKTOP-94ADH1G","HGL8081-1","lcx_ace"]:
    DEBUG_MODEL = True
print(fr" DEBUG_MODEL ： {DEBUG_MODEL}")
SHOW_OPENCV = True
SHOW_STEEL_PREDICT = False

CapTureBaseClass = Thread

class CapModelEnum(Enum):
    OPENCV=1
    AV=2
    SDK=3
    DEBUG=4
show_camera = False


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
