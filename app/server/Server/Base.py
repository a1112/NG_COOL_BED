import cv2
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException

from Configs.AppConfigs import app_configs
from Configs.CameraManageConfig import camera_manage_config
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Configs.GroupConfig import GroupConfig
from Configs.MappingConfig import MappingConfig
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
    cbc:CoolBedGroupConfig = camera_manage_config.group_dict[cool_bed_key]
    re_data = {}
    for g_key,g_config in cbc.groups_dict.items():
        g_config:GroupConfig
        map_config :MappingConfig = g_config.map_config
        re_data[g_key] = map_config.info
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
    cool_bed_data =  {key:item.get_info() for key, item in business_main.data_item_dict[cool_bed].items()}
    cool_bed_data["current"] = business_main.get_current_data(cool_bed)
    return cool_bed_data
    #  return business_main.data_map.get_info_by_cool_bed(cool_bed)


@app.get("/send_data")
async def send_data():
    return business_main.send_data


@app.get("/current_info")
def current_info():

    return business_main.current_info

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
    available = [p.name for p in cameras_root.iterdir() if p.is_dir()] if cameras_root.exists() else []
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
