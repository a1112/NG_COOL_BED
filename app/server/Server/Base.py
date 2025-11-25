import cv2
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException

from Configs.AppConfigs import app_configs
from Configs.CameraManageConfig import camera_manage_config
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Configs.GroupConfig import GroupConfig
from Configs.MappingConfig import MappingConfig
from Configs.CameraListConfig import camera_list_config
from ProjectManagement.Main import CoolBedThreadWorker
from Result.DataItem import DataItem
from ProjectManagement.Business import Business
from Globals import business_main, cool_bed_thread_worker_map, global_config
from CONFIG import debug_control, CALIBRATE_SELECT_FILE, CAMERA_CONFIG_FOLDER, SETTINGS_CONFIG_FILE, CURRENT_CALIBRATE
from fastapi.responses import StreamingResponse, FileResponse, Response

from Server.tool import noFindImageByte

business_main: Business

app = FastAPI(debug=False)
@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_data_item_info(data:DataItem):
    if data is None:
        return "w无数据，刷新后再尝试吧。"
    return {
        "key":data.group_key,
        "左侧辊道有板" : data.has_roll_steel_left,
        "右侧辊道有板" : data.has_roll_steel_right,
        "左侧冷床辊道有板" : data.has_cool_bed_steel_left,
        "右侧冷床辊道有板" : data.has_cool_bed_steel_right,
        "操作错误" : data.has_error,
        "左侧距离下辊道距离" : data.left_under_steel.y2_mm,
        "左侧距离辊道中心距离" : data.left_under_steel.to_roll_center_y,
        "steel_rect" : data.steel_info
    }

@app.get("/steel_msg")
def steel_info():
    di1:DataItem = business_main.data_item_l1
    di2:DataItem = business_main.data_item_l2
    return {
        "L1":get_data_item_info(di1),
        "L2":get_data_item_info(di2)
    }


@app.get("/info")
async def get_info():

    info = camera_manage_config.info
    info.update(
        {
            "app": app_configs.info,
            "debug": global_config.debug,
        }
    )

    return info


@app.get("/map/{cool_bed_key:str}")
async def get_map(cool_bed_key):
    if cool_bed_key not in camera_manage_config.group_dict:
        raise HTTPException(status_code=404, detail=f"cool_bed_key not found: {cool_bed_key}")
    cbc:CoolBedGroupConfig = camera_manage_config.group_dict[cool_bed_key]
    re_data = {}
    for g_key,g_config in cbc.groups_dict.items():
        g_config:GroupConfig
        map_config :MappingConfig = g_config.map_config
        re_data[g_key] = map_config.info
    return re_data


@app.get("/map")
async def get_map_all():
    """
    返回所有冷床的 map 信息（兼容前端未传 key 的旧调用方式）
    """
    re_data = {}
    for cool_bed_key, cbc in camera_manage_config.group_dict.items():
        cool_bed_map = {}
        for g_key, g_config in cbc.groups_dict.items():
            g_config: GroupConfig
            map_config: MappingConfig = g_config.map_config
            cool_bed_map[g_key] = map_config.info
        re_data[cool_bed_key] = cool_bed_map
    return re_data


@app.get("/image/{cool_bed:str}/{key:str}/{cap_index:int}/{show_mask:int}")
async def get_image(cool_bed:str, key:str, cap_index:int,show_mask=0):
    cool_bed_thread_worker = cool_bed_thread_worker_map[cool_bed]
    cool_bed_thread_worker:CoolBedThreadWorker
    index, cv_image = cool_bed_thread_worker.get_image(key,show_mask)
    if index < 0:
        return Response(content=noFindImageByte, media_type="image/jpg")
    _, encoded_image = cv2.imencode(".jpg", cv_image)
    # 返回图像响应
    return Response(content=encoded_image.tobytes(), media_type="image/jpeg")


@app.get("/data/{cool_bed:str}")
async def get_data(cool_bed:str):
    data_dict = business_main.data_item_dict if hasattr(business_main, "data_item_dict") else {}
    if cool_bed not in data_dict:
        raise HTTPException(status_code=404, detail=f"cool_bed not ready: {cool_bed}")
    cool_bed_data = {key: item.get_info() for key, item in data_dict[cool_bed].items()}
    if hasattr(business_main, "get_current_data"):
        cool_bed_data["current"] = business_main.get_current_data(cool_bed)
    return cool_bed_data


@app.get("/send_data")
async def send_data():
    return business_main.send_data


@app.get("/current_info")
def current_info():

    return business_main.current_info


def _derive_seq(cam_id: str):
    import re
    m = re.match(r"L(\d+)_([0-9]+)", cam_id, re.IGNORECASE)
    if not m:
        return None
    line = int(m.group(1))
    idx = int(m.group(2))
    return (line - 1) * 6 + idx


@app.get("/cameras")
async def get_cameras():
    """
    返回前端相机列表所需信息：
    camera, bed, ip, rtsp_url(若无则空), seq(推算), position(若无则空)
    """
    res = []
    cfg = getattr(camera_list_config, "config", {}) or {}
    for bed_key, bed_info in cfg.items():
        ip_list = (bed_info or {}).get("ipList", {}) or {}
        for cam_id, cam_info in ip_list.items():
            cam_info = cam_info or {}
            res.append({
                "camera": cam_id,
                "bed": bed_key,
                "ip": cam_info.get("ip", ""),
                "rtsp_url": cam_info.get("rtsp_url", ""),
                "seq": cam_info.get("seq") or _derive_seq(cam_id),
                "position": cam_info.get("position", ""),
                "enable": cam_info.get("enable", True),
            })
    return res


def _safe_calibrate_path(calibrate: str, name: str) -> Path:
    base = (CAMERA_CONFIG_FOLDER / "cameras" / calibrate).resolve()
    path = (base / name).resolve()
    try:
        path.relative_to(base)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid path")
    return path


def _load_calibrate_file(calibrate: str, filename: str):
    path = _safe_calibrate_path(calibrate, filename)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"{filename} not found for calibrate: {calibrate}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"failed to read {filename}") from exc


@app.get("/calibrate/label/{calibrate}/{cam_id}")
def get_calibrate_label(calibrate: str, cam_id: str):
    return _load_calibrate_file(calibrate, f"{cam_id}.json")


@app.get("/calibrate/image/{calibrate}/{image_name}")
def get_calibrate_image(calibrate: str, image_name: str):
    name = image_name
    if "." not in name:
        name += ".jpg"
    path = _safe_calibrate_path(calibrate, name)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"image not found: {name}")
    return FileResponse(path, media_type="image/jpeg")


@app.get("/calibrate/camera_manage/{calibrate}")
def get_calibrate_camera_manage(calibrate: str):
    return _load_calibrate_file(calibrate, "CameraManage.json")


@app.get("/calibrate/camera_manage")
def get_current_calibrate_camera_manage():
    return _load_calibrate_file(CURRENT_CALIBRATE, "CameraManage.json")


@app.get("/test_pre_image")
def test_pre_image():
    return debug_control.prev()

@app.get("/test_next_image")
def test_next_image():
    return debug_control.next()

@app.get("/save_cap")
def save_cap():
    business_main.save_cap()

@app.get("/save_one_cap")
def save_one_cap():
    return business_main.save_one_cap()


# ---------- Config APIs ----------
SETTINGS_ALLOWED_KEYS = {
    "serverUrl",
    "ipAddress",
    "modelType",
    "configPath",
    "currentConfig",
    "modelCategories",
    "selectedCategory",
    "selectedModel",
    "modelListDet",
    "modelListSeg",
    "testDataFolder",
}


def _load_json_file(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json_file(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/config/calibrate")
def get_calibrate_config():
    cameras_root = CAMERA_CONFIG_FOLDER / "cameras"
    if cameras_root.exists():
        available = [
            p.name for p in cameras_root.iterdir()
            if p.is_dir() and not p.name.startswith("__") and not p.name.startswith(".")
        ]
    else:
        available = []
    current = CURRENT_CALIBRATE
    return {"current": current, "available": available, "file": str(CALIBRATE_SELECT_FILE)}


@app.post("/config/calibrate")
def set_calibrate_config(payload: dict):
    target = payload.get("current")
    if not target or not isinstance(target, str):
        raise HTTPException(status_code=400, detail="current must be a non-empty string")
    cameras_root = CAMERA_CONFIG_FOLDER / "cameras"
    candidate = cameras_root / target
    if not candidate.is_dir():
        raise HTTPException(status_code=400, detail=f"calibrate folder not found: {candidate}")
    data = {"current": target}
    _save_json_file(CALIBRATE_SELECT_FILE, data)
    return {"ok": True, "current": target}


@app.get("/config/settings")
def get_settings():
    default = {
        "serverUrl": "",
        "ipAddress": "",
        "modelType": "",
        "configPath": "",
        "currentConfig": "",
        "modelCategories": ["目标检测", "分割"],
        "selectedCategory": "目标检测",
        "selectedModel": "",
        "modelListDet": [],
        "modelListSeg": [],
        "testDataFolder": "",
    }
    return _load_json_file(SETTINGS_CONFIG_FILE, default)


@app.post("/config/settings")
def set_settings(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be an object")
    settings = _load_json_file(SETTINGS_CONFIG_FILE, {})
    for k, v in payload.items():
        if k in SETTINGS_ALLOWED_KEYS:
            settings[k] = v
    _save_json_file(SETTINGS_CONFIG_FILE, settings)
    return {"ok": True, "settings": settings}


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6110)
