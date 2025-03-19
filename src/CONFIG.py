from pathlib import Path


# CONFIG
CONFIG_FOLDER = Path(__file__).parent.parent/"config"
if not CONFIG_FOLDER.is_dir():
    CONFIG_FOLDER = Path("D:/NG_CONFIG")

assert CONFIG_FOLDER.exists(), f"CONFIG_FOLDER 不存在： {CONFIG_FOLDER}"

print(CONFIG_FOLDER)

CAMERA_CONFIG_FOLDER = CONFIG_FOLDER / "camera"
IP_LIST_CAMERA_CONFIG = CONFIG_FOLDER / "camera"/"IpList.json"
CAMERA_MANAGE_CONFIG = CONFIG_FOLDER / "camera"/"CameraManage.json"

lOG_DIR = CONFIG_FOLDER / "log"
lOG_DIR.mkdir(exist_ok=True, parents=True)
encoding = "utf-8"