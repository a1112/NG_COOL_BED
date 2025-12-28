import time
from threading import Lock, Thread
from typing import Optional

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse
from tqdm import tqdm

from Configs.CameraManageConfig import camera_manage_config
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Configs.GlobalConfig import GlobalConfig
from Loger import logger
from ProjectManagement.Main import CoolBedThreadWorker
from Server.tool import noFindImageByte


def _resize_to_fit(image: np.ndarray, max_w: int = 0, max_h: int = 0) -> np.ndarray:
    if image is None:
        return image
    try:
        height, width = image.shape[:2]
    except Exception:
        return image

    max_w = int(max_w or 0)
    max_h = int(max_h or 0)
    if max_w <= 0 and max_h <= 0:
        return image
    if width <= 0 or height <= 0:
        return image

    scale_w = (max_w / width) if max_w > 0 else 1.0
    scale_h = (max_h / height) if max_h > 0 else 1.0
    scale = min(scale_w, scale_h, 1.0)
    if scale >= 0.999:
        return image

    new_w = max(1, int(width * scale))
    new_h = max(1, int(height * scale))
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _ensure_limited_range(frame):
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


def _prepare_frame_for_encode(frame: np.ndarray, w: int = 0, h: int = 0, color: str = "bgr") -> np.ndarray:
    try:
        frame = _ensure_limited_range(frame)
    except Exception:
        pass
    frame = _resize_to_fit(frame, w, h)
    if (color or "bgr").lower() == "rgb":
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception:
            pass
    return frame


class _MuxBuffer:
    def __init__(self):
        self._buf = bytearray()

    def write(self, data: bytes) -> int:
        self._buf.extend(data)
        return len(data)

    def flush(self) -> None:
        return None

    def pop(self) -> bytes:
        if not self._buf:
            return b""
        data = bytes(self._buf)
        self._buf.clear()
        return data


class CaptureService:
    def __init__(self, cool_bed_key: str):
        self.cool_bed_key = cool_bed_key
        self.config: CoolBedGroupConfig = camera_manage_config.group_dict[cool_bed_key]
        self.global_config = GlobalConfig()
        self.worker = CoolBedThreadWorker(cool_bed_key, self.config, self.global_config)
        if not self.worker.run_worker:
            raise RuntimeError(f"cool bed {cool_bed_key} not enabled in CameraManage.json")
        self._latest_payload = None
        self._payload_lock = Lock()
        self.app = FastAPI(debug=False)
        self._register_routes()
        self._start_collect_loop()

    def _start_collect_loop(self):
        thread = Thread(target=self._collect_loop, daemon=True)
        thread.start()

    def _collect_loop(self):
        pbar = tqdm(desc=f"{self.cool_bed_key} detect", unit="frame", dynamic_ncols=True)
        while True:
            steel_info = self.worker.get_steel_info()
            if not isinstance(steel_info, dict):
                continue
            payload = self._serialize_payload(steel_info)
            with self._payload_lock:
                self._latest_payload = payload
            pbar.update(1)

    def _serialize_payload(self, steel_info: dict) -> dict:
        groups = {}
        for group_key, result in steel_info.items():
            if result is None:
                groups[group_key] = None
                continue
            groups[group_key] = {
                "rec_list": result.rec_list,
                "ts": result.time,
            }
        return {
            "cool_bed": self.cool_bed_key,
            "timestamp": time.time(),
            "groups": groups,
        }

    def _get_latest_payload(self) -> dict:
        with self._payload_lock:
            payload = self._latest_payload
        if isinstance(payload, dict):
            return payload
        return {"cool_bed": self.cool_bed_key, "timestamp": 0.0, "groups": {}, "ready": False}

    def _register_routes(self):
        app = self.app

        @app.get("/")
        def root():
            return {"cool_bed": self.cool_bed_key, "ready": True}

        @app.get("/boxes")
        def get_boxes():
            return self._get_latest_payload()

        @app.get("/image/{cool_bed}/{key}/{cap_index}/{show_mask}")
        def get_image(
            cool_bed: str,
            key: str,
            cap_index: int,
            show_mask: int = 0,
            w: int = 0,
            h: int = 0,
            jpeg_quality: int = 80,
        ):
            if cool_bed != self.cool_bed_key:
                raise HTTPException(status_code=404, detail=f"cool_bed not found: {cool_bed}")
            if key not in self.worker.config.groups_dict:
                raise HTTPException(status_code=404, detail=f"group not found: {key}")
            index, cv_image = self.worker.get_latest_image(key, show_mask)
            source = "latest"
            if index < 0 or cv_image is None:
                index, cv_image = self.worker.get_image(key, show_mask)
                source = "processed"
            if index < 0 or cv_image is None:
                return Response(
                    content=noFindImageByte,
                    media_type="image/jpg",
                    headers={"Cache-Control": "no-store", "X-Image-Source": source},
                )
            jpeg_quality = int(jpeg_quality)
            jpeg_quality = max(10, min(95, jpeg_quality))
            frame_to_encode = _prepare_frame_for_encode(cv_image, w=int(w or 0), h=int(h or 0), color="bgr")
            ok, encoded_image = cv2.imencode(
                ".jpg",
                frame_to_encode,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
            )
            if not ok:
                return Response(
                    content=noFindImageByte,
                    media_type="image/jpg",
                    headers={"Cache-Control": "no-store", "X-Image-Source": source},
                )
            return Response(
                content=encoded_image.tobytes(),
                media_type="image/jpeg",
                headers={"Cache-Control": "no-store", "X-Image-Source": source},
            )

        @app.get("/capture/camera/{camera_id}")
        def get_camera_frame(camera_id: str, jpeg_quality: int = 80):
            capture = self.worker.camera_map.get(camera_id)
            if capture is None:
                raise HTTPException(status_code=404, detail=f"camera not found: {camera_id}")
            frame = capture.get_latest_frame()
            if frame is None:
                raise HTTPException(status_code=404, detail=f"camera frame not ready: {camera_id}")
            jpeg_quality = int(jpeg_quality)
            jpeg_quality = max(10, min(95, jpeg_quality))
            ok, encoded_image = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
            )
            if not ok:
                raise HTTPException(status_code=500, detail="failed to encode capture image")
            return Response(
                content=encoded_image.tobytes(),
                media_type="image/jpeg",
                headers={"Cache-Control": "no-store"},
            )

        def _video_stream(
            group_key: str,
            show_mask: int,
            fmt: str = "jpg",
            jpeg_quality: int = 80,
            w: int = 0,
            h: int = 0,
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
            w = int(w or 0)
            h = int(h or 0)

            while True:
                try:
                    _, cv_image = self.worker.get_latest_image(group_key, show_mask)
                except Exception:
                    cv_image = None
                if cv_image is None:
                    time.sleep(0.05)
                    continue
                frame_to_encode = _prepare_frame_for_encode(cv_image, w=w, h=h, color=color)
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
                frame_len = str(len(frame)).encode("ascii")
                yield (
                    boundary + b"\r\n"
                    b"Content-Type: " + content_type + b"\r\n"
                    b"Content-Length: " + frame_len + b"\r\n\r\n"
                    + frame + b"\r\n"
                )
                time.sleep(0.03)

        def _video_stream_ts(
            group_key: str,
            show_mask: int,
            fps: int = 25,
            crf: int = 28,
            preset: str = "ultrafast",
            w: int = 0,
            h: int = 0,
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
            w = int(w or 0)
            h = int(h or 0)

            width = None
            height = None
            while True:
                try:
                    _, cv_image = self.worker.get_latest_image(group_key, show_mask)
                except Exception:
                    cv_image = None
                if cv_image is None:
                    time.sleep(0.05)
                    continue
                if cv_image is not None and cv_image.ndim == 3 and cv_image.shape[2] == 3:
                    height, width = cv_image.shape[:2]
                    break

            if width is None or height is None:
                raise HTTPException(status_code=500, detail="no frames available")

            if w > 0 or h > 0:
                scale_w = (w / width) if w > 0 else 1.0
                scale_h = (h / height) if h > 0 else 1.0
                scale = min(scale_w, scale_h, 1.0)
                if scale < 0.999:
                    width = max(1, int(width * scale))
                    height = max(1, int(height * scale))

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
                        _, cv_image = self.worker.get_latest_image(group_key, show_mask)
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
                    video_frame.color_range = "mpeg"
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

        @app.get("/video/{cool_bed}/{key}/{show_mask}")
        def get_video_stream(
            cool_bed: str,
            key: str,
            show_mask: int = 0,
            fmt: str = "jpg",
            jpeg_quality: int = 80,
            fps: int = 10,
            crf: int = 28,
            preset: str = "ultrafast",
            w: int = 0,
            h: int = 0,
            color: str = "bgr",
        ):
            if cool_bed != self.cool_bed_key:
                raise HTTPException(status_code=404, detail=f"cool_bed not found: {cool_bed}")
            if key not in self.worker.config.groups_dict:
                raise HTTPException(status_code=404, detail=f"group not found: {key}")
            fmt_norm = (fmt or "jpg").strip().lower()
            if fmt_norm in {"ts", "mpegts", "h264", "h.264"}:
                return StreamingResponse(
                    _video_stream_ts(
                        key,
                        show_mask,
                        fps=fps,
                        crf=crf,
                        preset=preset,
                        w=w,
                        h=h,
                        color=color,
                    ),
                    media_type="video/mp2t",
                )
            return StreamingResponse(
                _video_stream(
                    key,
                    show_mask,
                    fmt=fmt,
                    jpeg_quality=jpeg_quality,
                    w=w,
                    h=h,
                    color=color,
                ),
                media_type="multipart/x-mixed-replace;boundary=frame",
            )

        @app.get("/video_ts/{cool_bed}/{key}/{show_mask}")
        def get_video_stream_ts(
            cool_bed: str,
            key: str,
            show_mask: int = 0,
            fps: int = 25,
            crf: int = 28,
            preset: str = "ultrafast",
            w: int = 0,
            h: int = 0,
            color: str = "bgr",
        ):
            if cool_bed != self.cool_bed_key:
                raise HTTPException(status_code=404, detail=f"cool_bed not found: {cool_bed}")
            if key not in self.worker.config.groups_dict:
                raise HTTPException(status_code=404, detail=f"group not found: {key}")
            return StreamingResponse(
                _video_stream_ts(key, show_mask, fps=fps, crf=crf, preset=preset, w=w, h=h, color=color),
                media_type="video/mp2t",
            )

    def run(self, host: str, port: int):
        logger.info("capture server start: %s -> %s:%s", self.cool_bed_key, host, port)
        uvicorn.run(self.app, host=host, port=port, log_level="info", access_log=True)
