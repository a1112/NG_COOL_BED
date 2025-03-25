import socket
from pathlib import Path

from threading import Thread
from multiprocessing import Process

# CONFIG
CONFIG_FOLDER = Path(__file__).parent.parent/"config"
if not CONFIG_FOLDER.is_dir():
    CONFIG_FOLDER = Path("D:/NG_CONFIG")

assert CONFIG_FOLDER.exists(), f"CONFIG_FOLDER 不存在： {CONFIG_FOLDER}"

print(CONFIG_FOLDER)

CAMERA_CONFIG_FOLDER = CONFIG_FOLDER / "camera"
IP_LIST_CAMERA_CONFIG = CONFIG_FOLDER / "camera"/"IpList.json"
CAMERA_MANAGE_CONFIG = CONFIG_FOLDER / "camera"/"CameraManage.json"

SAVE_CONFIG = CONFIG_FOLDER / "camera"/"Save.json"

lOG_DIR = CONFIG_FOLDER / "log"
lOG_DIR.mkdir(exist_ok=True, parents=True)
encoding = "utf-8"


DATA_FOLDER = CONFIG_FOLDER / "data"
DATA_FOLDER.mkdir(exist_ok=True, parents=True)
DEBUG_MODEL = False
print(f"hostname: {socket.gethostname()}")
if socket.gethostname() in ["MS-LGKRSZGOVODD", "DESKTOP-94ADH1G"]:
    DEBUG_MODEL = True



CapTureBaseClass = Thread
USE_OPENCV=False

DATA_FMT="%Y-%m-%d"
TIME_FMT="%H_%M_%S"

DATETIME_FMT = f"{DATA_FMT}-{TIME_FMT}"
IMAGE_SAVE_TYPE = "jpg"
APP_RUN = True