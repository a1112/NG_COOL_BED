import cv2
import json
import asyncio
import time
import math
import shutil
from pathlib import Path
from typing import Optional
import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import xml.etree.ElementTree as ET

import CONFIG
from Configs.AppConfigs import app_configs
from Configs.CameraManageConfig import camera_manage_config
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Configs.GroupConfig import GroupConfig
from Configs.MappingConfig import MappingConfig
from Configs.CameraListConfig import camera_list_config
from ProjectManagement.Main import CoolBedThreadWorker
from Result.DataItem import DataItem
from ProjectManagement.Business import Business
from ProjectManagement.PriorityManager import priority_registry
from Globals import business_main, cool_bed_thread_worker_map, global_config
from CONFIG import (
    debug_control,
    CALIBRATE_SELECT_FILE,
    CAMERA_CONFIG_FOLDER,
    SETTINGS_CONFIG_FILE,
    CURRENT_CALIBRATE,
    MappingPath,
    MODEL_FOLDER,
    FIRST_SAVE_FOLDER,
)
from fastapi.responses import StreamingResponse, FileResponse, Response
from CameraStreamer.ConversionImage import ConversionImage

import tool as common_tool
from Server.tool import noFindImageByte
from Server.alg_test_manager import alg_test_manager
from CommPlc import db5_reader, db6_sender
from Loger import logger

business_main: Business

app = FastAPI(debug=False)
@app.get("/")
def read_root():
    return {"Hello": "World"}


_last_stream_frame_cache = {}


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
    index, cv_image = cool_bed_thread_worker.get_latest_image(key, show_mask)
    source = "latest"
    if index < 0 or cv_image is None:
        index, cv_image = cool_bed_thread_worker.get_image(key, show_mask)
        source = "processed"
    if index < 0:
        return Response(
            content=noFindImageByte,
            media_type="image/jpg",
            headers={"Cache-Control": "no-store", "X-Image-Source": source},
        )
    _, encoded_image = cv2.imencode(".jpg", cv_image)
    # 返回图像响应
    return Response(
        content=encoded_image.tobytes(),
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store", "X-Image-Source": source},
    )


def _video_stream(
    worker: CoolBedThreadWorker,
    cool_bed: str,
    group_key: str,
    show_mask: int,
    fmt: str = "jpg",
    jpeg_quality: int = 80,
    color: str = "bgr",
):
    boundary = b"--frame"
    show_mask = int(show_mask)
    fmt = (fmt or "jpg").lower()
    if fmt == "jpeg":
        fmt = "jpg"
    if fmt not in {"jpg", "png"}:
        fmt = "jpg"
    jpeg_quality = int(jpeg_quality)
    jpeg_quality = max(10, min(95, jpeg_quality))
    content_type = b"image/png" if fmt == "png" else b"image/jpeg"
    color = (color or "bgr").lower()
    if color not in {"bgr", "rgb"}:
        color = "bgr"
    cache_key = (cool_bed, group_key, show_mask, fmt, jpeg_quality, color)
    cached = _last_stream_frame_cache.get(cache_key)
    if cached:
        if isinstance(cached, tuple) and len(cached) == 2:
            cached_ts, cached_frame = cached
        else:
            cached_ts, cached_frame = 0.0, cached
        if cached_frame and (time.time() - float(cached_ts or 0.0)) < 0.3:
            frame_len = str(len(cached_frame)).encode("ascii")
            yield (
                boundary + b"\r\n"
                b"Content-Type: " + content_type + b"\r\n"
                b"Content-Length: " + frame_len + b"\r\n\r\n"
                + cached_frame + b"\r\n"
            )
    while True:
        try:
            _, cv_image = worker.get_latest_image(group_key, show_mask)
        except Exception:
            cv_image = None
        if cv_image is None:
            time.sleep(0.05)
            continue
        frame_to_encode = _ensure_limited_range(cv_image)
        if color == "rgb":
            frame_to_encode = cv2.cvtColor(frame_to_encode, cv2.COLOR_BGR2RGB)
        if fmt == "png":
            ok, encoded_image = cv2.imencode(".png", frame_to_encode)
        else:
            ok, encoded_image = cv2.imencode(
                ".jpg",
                frame_to_encode,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
            )
        if not ok:
            continue
        frame = encoded_image.tobytes()
        _last_stream_frame_cache[cache_key] = (time.time(), frame)
        frame_len = str(len(frame)).encode("ascii")
        yield (
            boundary + b"\r\n"
            b"Content-Type: " + content_type + b"\r\n"
            b"Content-Length: " + frame_len + b"\r\n\r\n"
            + frame + b"\r\n"
        )
        time.sleep(0.03)


def _ensure_limited_range(frame):
    """
    Convert to uint8 and clamp to limited range (TV):
    - Y:   [16, 235]
    - U/V: [16, 240]
    """
    if frame is None:
        return frame
    if frame.ndim != 3 or frame.shape[2] != 3:
        return frame
    if frame.dtype != np.uint8:
        frame = cv2.convertScaleAbs(frame)
    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    y_channel = np.clip(yuv[:, :, 0], 16, 235)
    u_channel = np.clip(yuv[:, :, 1], 16, 240)
    v_channel = np.clip(yuv[:, :, 2], 16, 240)
    yuv = np.stack((y_channel, u_channel, v_channel), axis=2).astype(np.uint8, copy=False)
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

class _MuxBuffer:
    def __init__(self):
        self._buf = bytearray()

    def write(self, data: bytes) -> int:
        self._buf.extend(data)
        return len(data)

    def flush(self) -> None:  # file-like compatibility
        return None

    def pop(self) -> bytes:
        if not self._buf:
            return b""
        data = bytes(self._buf)
        self._buf.clear()
        return data


def _video_stream_ts(
    worker: CoolBedThreadWorker,
    group_key: str,
    show_mask: int,
    fps: int = 25,
    crf: int = 28,
    preset: str = "ultrafast",
    color: str = "bgr",
):
    try:
        import av  # type: ignore
    except Exception as exc:
        raise HTTPException(status_code=500, detail="PyAV not available") from exc

    fps = int(fps)
    fps = max(1, min(60, fps))
    crf = int(crf)
    crf = max(0, min(51, crf))
    preset = (preset or "ultrafast").strip()
    color = (color or "bgr").lower()
    if color not in {"bgr", "rgb"}:
        color = "bgr"
    show_mask = int(show_mask)

    width = None
    height = None
    while True:
        try:
            _, cv_image = worker.get_latest_image(group_key, show_mask)
        except Exception:
            cv_image = None
        if cv_image is None:
            time.sleep(0.05)
            continue
        if cv_image is not None and cv_image.ndim == 3 and cv_image.shape[2] == 3:
            height, width = cv_image.shape[:2]
            break

    pad_right = 1 if int(width) % 2 else 0
    pad_bottom = 1 if int(height) % 2 else 0
    enc_width = int(width) + pad_right
    enc_height = int(height) + pad_bottom

    mux_buffer = _MuxBuffer()
    output = av.open(mux_buffer, mode="w", format="mpegts")
    stream = output.add_stream("libx264", rate=fps)
    stream.width = enc_width
    stream.height = enc_height
    stream.pix_fmt = "yuv420p"
    # Limited range (TV) to match the 16-235 clamping above.
    stream.codec_context.color_range = 1
    stream.options = {
        "preset": preset,
        "tune": "zerolatency",
        "crf": str(crf),
    }

    try:
        last_time = 0.0
        while True:
            if fps > 0:
                now = time.time()
                min_dt = 1.0 / fps
                if last_time and now - last_time < min_dt:
                    time.sleep(min_dt - (now - last_time))
                last_time = time.time()

            try:
                _, cv_image = worker.get_latest_image(group_key, show_mask)
            except Exception:
                cv_image = None
            if cv_image is None:
                continue

            frame_to_encode = _ensure_limited_range(cv_image)
            if frame_to_encode is None:
                continue
            if frame_to_encode.ndim != 3 or frame_to_encode.shape[2] != 3:
                continue
            if frame_to_encode.dtype != np.uint8:
                frame_to_encode = frame_to_encode.astype(np.uint8, copy=False)
            if frame_to_encode.shape[1] != width or frame_to_encode.shape[0] != height:
                frame_to_encode = cv2.resize(frame_to_encode, (int(width), int(height)))
            if pad_right or pad_bottom:
                frame_to_encode = cv2.copyMakeBorder(
                    frame_to_encode,
                    0,
                    pad_bottom,
                    0,
                    pad_right,
                    borderType=cv2.BORDER_CONSTANT,
                    value=(0, 0, 0),
                )

            if color == "rgb":
                frame_to_encode = cv2.cvtColor(frame_to_encode, cv2.COLOR_BGR2RGB)
                video_frame = av.VideoFrame.from_ndarray(frame_to_encode, format="rgb24")
            else:
                video_frame = av.VideoFrame.from_ndarray(frame_to_encode, format="bgr24")
            for packet in stream.encode(video_frame):
                output.mux(packet)
                chunk = mux_buffer.pop()
                if chunk:
                    yield chunk
    finally:
        try:
            for packet in stream.encode(None):
                output.mux(packet)
                chunk = mux_buffer.pop()
                if chunk:
                    yield chunk
        except Exception:
            pass
        try:
            output.close()
        except Exception:
            pass


@app.get("/video/{cool_bed:str}/{key:str}/{show_mask:int}")
async def get_video_stream(
    cool_bed: str,
    key: str,
    show_mask: int = 0,
    fmt: str = "jpg",
    jpeg_quality: int = 80,
    fps: int = 4,
    crf: int = 28,
    preset: str = "ultrafast",
    color: str = "bgr",
):
    if cool_bed not in cool_bed_thread_worker_map:
        raise HTTPException(status_code=404, detail=f"cool_bed not found: {cool_bed}")
    worker = cool_bed_thread_worker_map[cool_bed]
    worker: CoolBedThreadWorker
    if key not in worker.config.groups_dict:
        raise HTTPException(status_code=404, detail=f"group not found: {key}")
    fmt_norm = (fmt or "jpg").strip().lower()
    if fmt_norm in {"ts", "mpegts", "h264", "h.264"}:
        return StreamingResponse(
            _video_stream_ts(worker, key, show_mask, fps=fps, crf=crf, preset=preset, color=color),
            media_type="video/mp2t",
        )
    return StreamingResponse(
        _video_stream(
            worker,
            cool_bed,
            key,
            show_mask,
            fmt=fmt,
            jpeg_quality=jpeg_quality,
            color=color,
        ),
        media_type="multipart/x-mixed-replace;boundary=frame",
    )


@app.get("/video_ts/{cool_bed:str}/{key:str}/{show_mask:int}")
async def get_video_stream_ts(
    cool_bed: str,
    key: str,
    show_mask: int = 0,
    fps: int = 25,
    crf: int = 28,
    preset: str = "ultrafast",
    color: str = "bgr",
):
    if cool_bed not in cool_bed_thread_worker_map:
        raise HTTPException(status_code=404, detail=f"cool_bed not found: {cool_bed}")
    worker = cool_bed_thread_worker_map[cool_bed]
    worker: CoolBedThreadWorker
    if key not in worker.config.groups_dict:
        raise HTTPException(status_code=404, detail=f"group not found: {key}")
    return StreamingResponse(
        _video_stream_ts(worker, key, show_mask, fps=fps, crf=crf, preset=preset, color=color),
        media_type="video/mp2t",
    )


@app.get("/data/{cool_bed:str}")
async def get_data(cool_bed:str):
    return _get_data_payload(cool_bed)


@app.get("/send_data")
async def send_data():
    return _sanitize_json(business_main.send_data)


@app.websocket("/ws/send_data")
async def ws_send_data(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = business_main.send_data
            try:
                await websocket.send_text(_safe_json_dumps(payload))
            except WebSocketDisconnect:
                break
            except Exception as exc:  # pragma: no cover - runtime only
                logger.error("ws/send_data send error: %s", exc)
            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        pass


def _sanitize_json(value):
    if isinstance(value, dict):
        return {str(k): _sanitize_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_json(v) for v in value]
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, (bytes, bytearray, memoryview)):
        return str(bytes(value))
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass
    if hasattr(value, "item"):
        try:
            return _sanitize_json(value.item())
        except Exception:
            pass
    return value


def _safe_json_dumps(payload: dict) -> str:
    try:
        return json.dumps(payload, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError):
        return json.dumps(_sanitize_json(payload), ensure_ascii=False, allow_nan=False)


def _get_db6_payload() -> dict:
    last_bytes = getattr(db6_sender, "last_bytes", b"") or b""
    last_data_dict = getattr(db6_sender, "last_data_dict", {}) or {}
    safe_data = dict(last_data_dict)
    return {
        "bytes": str(bytes(last_bytes)),
        "data": safe_data,
    }


@app.get("/db6_data")
async def db6_data():
    return _sanitize_json(_get_db6_payload())


@app.websocket("/ws/db6_data")
async def ws_db6_data(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = _get_db6_payload()
            try:
                await websocket.send_text(_safe_json_dumps(payload))
            except WebSocketDisconnect:
                break
            except Exception as exc:  # pragma: no cover - runtime only
                logger.error("ws/db6_data send error: %s", exc)
            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        pass


@app.get("/current_info")
def current_info():

    return business_main.current_info


@app.get("/priority/status")
def get_priority_status():
    return priority_registry.dump()


@app.post("/priority/shield")
def set_priority_shield(payload: Optional[dict] = None):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be object")
    cool_bed = payload.get("cool_bed")
    group_key = payload.get("group")
    shield = payload.get("shield")
    if not isinstance(cool_bed, str) or not cool_bed:
        raise HTTPException(status_code=400, detail="cool_bed required")
    if not isinstance(group_key, str) or not group_key:
        raise HTTPException(status_code=400, detail="group required")
    if not isinstance(shield, bool):
        raise HTTPException(status_code=400, detail="shield must be boolean")
    if cool_bed not in camera_manage_config.group_dict:
        raise HTTPException(status_code=404, detail=f"cool_bed not found: {cool_bed}")
    try:
        camera_manage_config.set_group_shield(cool_bed, group_key, shield)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    priority_registry.update_shield(cool_bed, group_key, shield)
    return {
        "ok": True,
        "cool_bed": cool_bed,
        "group": group_key,
        "shield": shield,
    }


def _derive_seq(cam_id: str):
    import re
    m = re.match(r"L(\d+)_([0-9]+)", cam_id, re.IGNORECASE)
    if not m:
        return None
    line = int(m.group(1))
    idx = int(m.group(2))
    return (line - 1) * 6 + idx


def _rtsp_url_from_config(ip: str, cam_info: dict) -> str:
    """
    Build RTSP url for frontend display/playback.
    If config already provides `rtsp_url`, use it; otherwise build from ip + credentials.
    """
    from urllib.parse import quote

    ip = (ip or "").strip()
    if not ip:
        return ""

    cam_info = cam_info or {}
    explicit = cam_info.get("rtsp_url", "")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()

    user = cam_info.get("rtsp_user", "admin")
    password = cam_info.get("rtsp_pass", "ng123456")
    path = cam_info.get("rtsp_path", "/stream")
    if not isinstance(path, str) or not path:
        path = "/stream"
    if not path.startswith("/"):
        path = "/" + path

    user = quote(str(user or ""), safe="")
    password = quote(str(password or ""), safe="")
    if user and password:
        return f"rtsp://{user}:{password}@{ip}{path}"
    return f"rtsp://{ip}{path}"


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
            ip = cam_info.get("ip", "")
            rtsp_url = _rtsp_url_from_config(ip, cam_info)
            res.append({
                "camera": cam_id,
                "bed": bed_key,
                "ip": ip,
                "rtsp_url": rtsp_url,
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


def _safe_calibrate_folder(calibrate: str) -> Path:
    base = (CAMERA_CONFIG_FOLDER / "cameras").resolve()
    folder = (base / calibrate).resolve()
    try:
        folder.relative_to(base)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid calibrate folder")
    if not folder.is_dir():
        raise HTTPException(status_code=404, detail=f"calibrate folder not found: {calibrate}")
    return folder


def _safe_mapping_folder(calibrate: str) -> Path:
    base = MappingPath.resolve()
    folder = (base / calibrate).resolve()
    try:
        folder.relative_to(base)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid mapping folder")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _find_group_config(camera_manage: dict, group_key: str) -> dict:
    group_root = (camera_manage or {}).get("group") or {}
    for bed_key, bed_cfg in group_root.items():
        bed_cfg = bed_cfg or {}
        groups = bed_cfg.get("group") or []
        if isinstance(groups, dict):
            groups = list(groups.values())
        for g in groups:
            g = g or {}
            if g.get("key") == group_key:
                return g
    raise HTTPException(status_code=404, detail=f"group not found: {group_key}")


def _update_mapping_xml_size(xml_path: Path, width: int, height: int) -> None:
    if not xml_path.is_file():
        return
    try:
        root = ET.fromstring(xml_path.read_text(encoding="utf-8"))
        size_node = root.find("size")
        if size_node is None:
            return
        w_node = size_node.find("width")
        h_node = size_node.find("height")
        if w_node is not None:
            w_node.text = str(int(width))
        if h_node is not None:
            h_node.text = str(int(height))
        xml_path.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
    except Exception:
        return


def _safe_mapping_path(calibrate: str, filename: str) -> Path:
    base = (MappingPath / calibrate).resolve()
    path = (base / filename).resolve()
    try:
        path.relative_to(base)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid mapping path")
    return path


def _sdk_capture_camera_path(camera_id: str) -> Path:
    base = (FIRST_SAVE_FOLDER / "camera").resolve()
    name = f"{camera_id}.jpg"
    path = (base / name).resolve()
    try:
        path.relative_to(base)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid camera id") from exc
    return path


CAPTURE_TMP_FOLDER = CAMERA_CONFIG_FOLDER / "capture_tmp"


def _safe_capture_tmp_path(calibrate: str, camera_id: str, suffix: str = ".jpg") -> Path:
    _safe_calibrate_folder(calibrate)
    base = (CAPTURE_TMP_FOLDER / calibrate).resolve()
    base.mkdir(parents=True, exist_ok=True)
    name = f"{camera_id}{suffix}"
    path = (base / name).resolve()
    try:
        path.relative_to(base)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid camera id") from exc
    return path


def _find_latest_camera_frame(camera_id: str):
    for worker in (cool_bed_thread_worker_map or {}).values():
        try:
            capture = getattr(worker, "camera_map", {}).get(camera_id)
            if capture is None:
                continue
            frame = capture.get_latest_frame()
            if frame is not None:
                return frame
        except Exception:
            continue
    for worker in (cool_bed_thread_worker_map or {}).values():
        try:
            frames = worker.snapshot_camera_frames()
            if camera_id in frames:
                return frames[camera_id]
        except Exception:
            continue
    return None


@app.get("/calibrate/label/{calibrate}/{cam_id}")
def get_calibrate_label(calibrate: str, cam_id: str):
    return _load_calibrate_file(calibrate, f"{cam_id}.json")


@app.post("/calibrate/label/save")
def save_calibrate_label(payload: dict):
    calibrate = payload.get("calibrate") or CURRENT_CALIBRATE
    cam_id = payload.get("camera")
    if not cam_id:
        raise HTTPException(status_code=400, detail="camera required")
    data = payload.get("data")
    if data is None:
        raise HTTPException(status_code=400, detail="data required")
    path = _safe_calibrate_path(calibrate, f"{cam_id}.json")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="failed to save label") from exc
    return {"ok": True, "path": str(path)}


@app.get("/calibrate/image/{calibrate}/{image_name}")
def get_calibrate_image(calibrate: str, image_name: str):
    name = image_name
    if "." not in name:
        name += ".jpg"
    path = _safe_calibrate_path(calibrate, name)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"image not found: {name}")
    return FileResponse(path, media_type="image/jpeg")


@app.get("/calibrate/capture/preview/{calibrate}/{camera_id}")
def get_calibrate_capture_preview(calibrate: str, camera_id: str):
    path = _safe_capture_tmp_path(calibrate, camera_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"capture preview not found: {camera_id}")
    return FileResponse(path, media_type="image/jpeg")


@app.post("/calibrate/capture")
def capture_calibrate_camera(payload: Optional[dict] = None):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be object")
    folder = payload.get("folder") or CURRENT_CALIBRATE
    camera_id = payload.get("camera")
    if not isinstance(folder, str) or not folder.strip():
        raise HTTPException(status_code=400, detail="folder must be string")
    if not isinstance(camera_id, str) or not camera_id.strip():
        raise HTTPException(status_code=400, detail="camera must be string")
    folder = folder.strip()
    camera_id = camera_id.strip()

    _safe_calibrate_folder(folder)
    frame = _find_latest_camera_frame(camera_id)
    if frame is None:
        raise HTTPException(status_code=404, detail=f"camera frame not ready: {camera_id}")
    out_path = _safe_capture_tmp_path(folder, camera_id)
    ok = cv2.imwrite(str(out_path), frame)
    if not ok:
        raise HTTPException(status_code=500, detail="failed to write capture image")
    logger.info("calibrate capture: folder=%s camera=%s -> %s", folder, camera_id, out_path)
    return {"ok": True, "folder": folder, "camera": camera_id, "path": str(out_path)}


@app.post("/calibrate/capture/save")
def save_calibrate_capture(payload: Optional[dict] = None):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be object")
    folder = payload.get("folder") or CURRENT_CALIBRATE
    if not isinstance(folder, str) or not folder.strip():
        raise HTTPException(status_code=400, detail="folder must be string")
    folder = folder.strip()

    _safe_calibrate_folder(folder)
    staged_dir = (CAPTURE_TMP_FOLDER / folder).resolve()
    if not staged_dir.is_dir():
        raise HTTPException(status_code=404, detail="no captured images staged")

    saved = 0
    for staged in staged_dir.glob("*.jpg"):
        dest = _safe_calibrate_path(folder, staged.name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, dest)
        saved += 1
    if saved:
        for staged in staged_dir.glob("*.jpg"):
            try:
                staged.unlink(missing_ok=True)
            except Exception:
                continue
    logger.info("calibrate capture save: folder=%s count=%s", folder, saved)
    return {"ok": True, "folder": folder, "count": saved}


@app.post("/calibrate/image/replace")
def replace_calibrate_image(payload: Optional[dict] = None):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be object")
    folder = payload.get("folder") or CURRENT_CALIBRATE
    camera_id = payload.get("camera")
    source = payload.get("source")
    if not isinstance(folder, str) or not folder.strip():
        raise HTTPException(status_code=400, detail="folder must be string")
    if not isinstance(camera_id, str) or not camera_id.strip():
        raise HTTPException(status_code=400, detail="camera must be string")
    if not isinstance(source, str) or not source.strip():
        raise HTTPException(status_code=400, detail="source must be string")
    folder = folder.strip()
    camera_id = camera_id.strip()
    source = source.strip()

    _safe_calibrate_folder(folder)

    if source == "first_save":
        src = _sdk_capture_camera_path(camera_id)
        if not src.is_file():
            raise HTTPException(status_code=404, detail="first_save image not found")
    elif source == "capture":
        src = _safe_capture_tmp_path(folder, camera_id)
        if not src.is_file():
            raise HTTPException(status_code=404, detail="capture image not found")
    else:
        raise HTTPException(status_code=400, detail="invalid source")

    dest = _safe_calibrate_path(folder, f"{camera_id}.jpg")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    logger.info("calibrate image replace: folder=%s camera=%s source=%s", folder, camera_id, source)
    return {"ok": True, "folder": folder, "camera": camera_id, "source": source}


@app.get("/capture/rtsp/{camera_id}")
def get_rtsp_capture_image(camera_id: str):
    path = _sdk_capture_camera_path(camera_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"capture not found: {camera_id}")
    return FileResponse(path, media_type="image/jpeg")


@app.get("/calibrate/mapping/{calibrate}/{file_path:path}")
def get_calibrate_mapping_file(calibrate: str, file_path: str):
    path = _safe_mapping_path(calibrate, file_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"mapping file not found: {file_path}")
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".bmp"}:
        return FileResponse(path, media_type="image/jpeg")
    media = "application/xml" if suffix == ".xml" else "text/plain"
    return Response(content=path.read_bytes(), media_type=media)


@app.get("/calibrate/camera_manage/{calibrate}")
def get_calibrate_camera_manage(calibrate: str):
    return _load_calibrate_file(calibrate, "CameraManage.json")


@app.get("/calibrate/camera_manage")
def get_current_calibrate_camera_manage():
    return _load_calibrate_file(CURRENT_CALIBRATE, "CameraManage.json")


@app.post("/calibrate/perspective/refresh")
def refresh_calibrate_perspective(payload: Optional[dict] = None):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be object")
    folder = payload.get("folder") or CURRENT_CALIBRATE
    group_key = payload.get("group")
    if not isinstance(folder, str) or not folder.strip():
        raise HTTPException(status_code=400, detail="folder must be string")
    if not isinstance(group_key, str) or not group_key.strip():
        raise HTTPException(status_code=400, detail="group must be string")
    folder = folder.strip()
    group_key = group_key.strip()

    calibrate_root = _safe_calibrate_folder(folder)
    camera_manage = _load_calibrate_file(folder, "CameraManage.json")
    group_cfg = _find_group_config(camera_manage, group_key)
    camera_list = group_cfg.get("camera_list") or []
    size_list = group_cfg.get("size_list") or []
    if not camera_list or not size_list or len(camera_list) != len(size_list):
        raise HTTPException(status_code=400, detail="invalid group camera/size list")

    images = []
    for cam_id, size in zip(camera_list, size_list):
        if not isinstance(cam_id, str) or not cam_id:
            raise HTTPException(status_code=400, detail="invalid camera id")
        try:
            width, height = int(size[0]), int(size[1])
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"invalid size for {cam_id}") from exc

        img_path = _safe_calibrate_path(folder, f"{cam_id}.jpg")
        if not img_path.is_file():
            img_path = _safe_calibrate_path(folder, f"{cam_id}.png")
        if not img_path.is_file():
            raise HTTPException(status_code=404, detail=f"camera image not found: {cam_id}")
        frame = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=500, detail=f"failed to read image: {cam_id}")

        conv = ConversionImage(cam_id, width, height, calibrate_root=calibrate_root)
        warped = conv.image_conversion(frame)
        images.append(warped)

    joined = np.hstack(images) if len(images) > 1 else images[0]
    mapping_folder = _safe_mapping_folder(folder)
    out_jpg = (mapping_folder / f"{group_key}.jpg").resolve()
    ok = cv2.imwrite(str(out_jpg), joined)
    if not ok:
        raise HTTPException(status_code=500, detail="failed to write mapping image")

    _update_mapping_xml_size(mapping_folder / f"{group_key}.xml", int(joined.shape[1]), int(joined.shape[0]))
    return {"ok": True, "image": str(out_jpg), "size": {"width": int(joined.shape[1]), "height": int(joined.shape[0])}}


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


@app.get("/debug/opencv_display")
def get_opencv_display_state():
    return {"enable": CONFIG.SHOW_OPENCV}


@app.post("/debug/opencv_display")
def set_opencv_display_state(payload: Optional[dict] = None):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be object")
    enable = payload.get("enable")
    if not isinstance(enable, bool):
        raise HTTPException(status_code=400, detail="enable must be boolean")
    common_tool.set_show_cv2_enabled(enable)
    return {"ok": True, "enable": CONFIG.SHOW_OPENCV}


@app.get("/debug/predict_display")
def get_predict_display_state():
    return {"enable": getattr(CONFIG, "SHOW_STEEL_PREDICT", True)}


@app.post("/debug/predict_display")
def set_predict_display_state(payload: Optional[dict] = None):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be object")
    enable = payload.get("enable")
    if not isinstance(enable, bool):
        raise HTTPException(status_code=400, detail="enable must be boolean")
    CONFIG.SHOW_STEEL_PREDICT = enable
    return {"ok": True, "enable": CONFIG.SHOW_STEEL_PREDICT}


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


# ---------- Algorithm test APIs ----------
@app.get("/alg/models")
def list_alg_models():
    return {
        "models": alg_test_manager.list_models(),
        "folder": str(MODEL_FOLDER.resolve()),
    }


@app.post("/alg/test/start")
def start_alg_test(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be object")
    return alg_test_manager.start_job(payload)


@app.post("/alg/test/stop")
def stop_alg_test(payload: Optional[dict] = None):
    task_id = payload.get("task_id") if isinstance(payload, dict) else None
    return alg_test_manager.stop_job(task_id)


@app.websocket("/alg/test/progress")
async def alg_progress(websocket: WebSocket):
    await alg_test_manager.handle_websocket(websocket)


def _auto_mode_value(snapshot: dict, cool_bed: str):
    if not isinstance(snapshot, dict):
        return None
    key = cool_bed.upper()
    if key == "L1":
        return snapshot.get("O_NAI_W1_spare5")
    if key == "L2":
        return snapshot.get("O_NAI_W1_spare6")
    return None


def _auto_mode_label(value) -> str:
    if value is True:
        return "自动"
    if value is False:
        return "手动"
    return "调整"


def _get_data_payload(cool_bed: str) -> dict:
    data_dict = business_main.data_item_dict if hasattr(business_main, "data_item_dict") else {}
    if cool_bed not in data_dict:
        raise HTTPException(status_code=404, detail=f"cool_bed not ready: {cool_bed}")
    cool_bed_data = {key: item.get_info() for key, item in data_dict[cool_bed].items()}
    if hasattr(business_main, "get_current_data"):
        cool_bed_data["current"] = business_main.get_current_data(cool_bed)
    controller = priority_registry.get_controller(cool_bed)
    for key, info in cool_bed_data.items():
        if key == "current" or not isinstance(info, dict):
            continue
        state = controller.state_for(key) if controller else None
        if not state:
            continue
        info["priority_level"] = state.level
        info["priority_reason"] = state.reason
        info["shielded"] = state.shielded
    auto_snapshot = {}
    try:
        auto_snapshot = db5_reader.snapshot() if db5_reader else {}
    except Exception:
        auto_snapshot = {}
    auto_value = _auto_mode_value(auto_snapshot, cool_bed)
    auto_label = _auto_mode_label(auto_value)
    for info in cool_bed_data.values():
        if isinstance(info, dict):
            info["auto_mode"] = auto_label
            info["auto_mode_value"] = auto_value
    return cool_bed_data


@app.websocket("/ws/data/{cool_bed}")
async def ws_data(cool_bed: str, websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                payload = _get_data_payload(cool_bed)
                await websocket.send_text(json.dumps(payload, ensure_ascii=False))
            except HTTPException as exc:
                await websocket.send_text(json.dumps({"error": exc.detail}, ensure_ascii=False))
                await asyncio.sleep(1.0)
                continue
            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        pass


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6110)
