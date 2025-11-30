import asyncio
import json
import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Dict, List, Optional, Set, Tuple

import cv2
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from ultralytics import YOLO

import CONFIG
from alg.YoloModelResults import YoloModelResults

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
IOU_THRESHOLD = 0.5


def _sanitize_folder_name(text: str) -> str:
    if not text:
        return "empty"
    safe = []
    for ch in text:
        safe.append(ch if ch.isalnum() or ch in ("-", "_") else "_")
    slug = "".join(safe).strip("_")
    return slug or "misc"


def _list_image_files(target: Path) -> List[Path]:
    files: List[Path] = []
    for path in target.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(path)
    return sorted(files)


def _reserve_path(path: Path) -> Path:
    if not path.exists():
        return path
    index = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def _pascal_voc_dict(image_name: str, width: int, height: int, boxes: List[dict]):
    return {
        "annotation": {
            "folder": "",
            "filename": image_name,
            "source": {"database": "Unknown"},
            "size": {"width": width, "height": height, "depth": 3},
            "segmented": 0,
            "object": [
                {
                    "name": box["label"],
                    "pose": "Unspecified",
                    "truncated": 0,
                    "difficult": 0,
                    "bndbox": {
                        "xmin": int(box["bbox"][0]),
                        "ymin": int(box["bbox"][1]),
                        "xmax": int(box["bbox"][2]),
                        "ymax": int(box["bbox"][3]),
                    },
                }
                for box in boxes
            ],
        }
    }


def _save_pascal_voc_xml(path: Path, image_name: str, width: int, height: int, boxes: List[dict]):
    from xml.etree.ElementTree import Element, SubElement, ElementTree

    annotation = Element("annotation")
    SubElement(annotation, "folder").text = path.parent.name
    SubElement(annotation, "filename").text = image_name
    source = SubElement(annotation, "source")
    SubElement(source, "database").text = "Unknown"
    size = SubElement(annotation, "size")
    SubElement(size, "width").text = str(width)
    SubElement(size, "height").text = str(height)
    SubElement(size, "depth").text = "3"
    SubElement(annotation, "segmented").text = "0"

    for box in boxes:
        obj = SubElement(annotation, "object")
        SubElement(obj, "name").text = box["label"]
        SubElement(obj, "pose").text = "Unspecified"
        SubElement(obj, "truncated").text = "0"
        SubElement(obj, "difficult").text = "0"
        bndbox = SubElement(obj, "bndbox")
        SubElement(bndbox, "xmin").text = str(int(box["bbox"][0]))
        SubElement(bndbox, "ymin").text = str(int(box["bbox"][1]))
        SubElement(bndbox, "xmax").text = str(int(box["bbox"][2]))
        SubElement(bndbox, "ymax").text = str(int(box["bbox"][3]))

    tree = ElementTree(annotation)
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(path, encoding="utf-8")


def _bbox_iou(a: List[float], b: List[float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    if inter_area <= 0:
        return 0.0
    area_a = max(0.0, (ax2 - ax1)) * max(0.0, (ay2 - ay1))
    area_b = max(0.0, (bx2 - bx1)) * max(0.0, (by2 - by1))
    union = area_a + area_b - inter_area
    if union <= 0:
        return 0.0
    return inter_area / union


def _analyze_boxes(boxes: List[dict], threshold: float):
    labels = [box["label"] for box in boxes]
    unique_labels = sorted(set(labels))
    combo = "_".join(unique_labels) if unique_labels else "empty"
    low_conf = any(box["conf"] < threshold for box in boxes)
    overlap_same: Set[str] = set()
    overlap_diff: Set[str] = set()
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            iou = _bbox_iou(boxes[i]["bbox"], boxes[j]["bbox"])
            if iou >= IOU_THRESHOLD:
                if boxes[i]["label"] == boxes[j]["label"]:
                    overlap_same.add(boxes[i]["label"])
                else:
                    pair = "_".join(sorted({boxes[i]["label"], boxes[j]["label"]}))
                    overlap_diff.add(pair)
    return {
        "combo": combo,
        "low_conf": low_conf,
        "overlap_same": overlap_same,
        "overlap_diff": overlap_diff,
        "has_boxes": len(boxes) > 0,
    }


@dataclass
class AlgTestJob:
    id: str
    model_path: Path
    target: Path
    output: Path
    threshold: float
    mode: str
    options: Dict[str, bool]
    manager: "AlgTestManager"
    total: int = 0
    processed: int = 0
    errors: int = 0
    started_at: float = field(default_factory=time.monotonic)
    stop_event: Event = field(default_factory=Event)
    running: bool = True
    summary: Dict[str, int] = field(default_factory=lambda: {
        "normal": 0,
        "abnormal": 0,
        "skipped": 0,
        "empty": 0,
    })
    status: str = "初始化"

    def should_classify(self) -> bool:
        return bool(self.options.get("classify_save", True))

    def should_save_label(self) -> bool:
        return bool(self.options.get("save_label", False))

    def priority_mode(self) -> bool:
        return bool(self.options.get("prioritize", False))

    def image_mode(self) -> str:
        return "move" if self.mode == "move" else "copy"

    def eta_seconds(self) -> Optional[float]:
        elapsed = max(0.0001, time.monotonic() - self.started_at)
        speed = self.processed / elapsed if elapsed > 0 else 0.0
        if speed <= 0:
            return None
        remaining = max(0, self.total - self.processed)
        return remaining / speed

    def current_speed(self) -> float:
        elapsed = max(0.0001, time.monotonic() - self.started_at)
        return self.processed / elapsed if elapsed > 0 else 0.0

    def build_payload(self, message: str = "", finished: bool = False):
        eta = self.eta_seconds()
        payload = {
            "task_id": self.id,
            "status": self.status,
            "done": self.processed,
            "total": self.total,
            "speed": round(self.current_speed(), 4),
            "eta": None if eta is None else eta,
            "errors": self.errors,
            "message": message,
            "finished": finished,
            "summary": self.summary,
        }
        return payload


class AlgTestManager:
    def __init__(self):
        self._job_lock = Lock()
        self._current_job: Optional[AlgTestJob] = None
        self._listeners: Dict[int, Dict[str, object]] = {}
        self._listeners_lock = Lock()
        self._last_payload = {"task_id": None, "status": "idle"}

    # ------------ model listing ------------
    def list_models(self) -> List[str]:
        models = []
        if CONFIG.MODEL_FOLDER.exists():
            for path in CONFIG.MODEL_FOLDER.iterdir():
                if path.is_file() and path.suffix.lower() in {".pt", ".onnx"}:
                    models.append(path.name)
        return sorted(models)

    # ------------ websocket management ------------
    async def handle_websocket(self, websocket: WebSocket):
        await websocket.accept()
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()
        listener_id = id(websocket)
        with self._listeners_lock:
            self._listeners[listener_id] = {
                "websocket": websocket,
                "queue": queue,
                "loop": loop,
            }
        if self._last_payload:
            await queue.put(self._last_payload)
        try:
            while True:
                payload = await queue.get()
                await websocket.send_text(json.dumps(payload, ensure_ascii=False))
        except WebSocketDisconnect:
            pass
        finally:
            with self._listeners_lock:
                self._listeners.pop(listener_id, None)

    def _broadcast(self, payload: dict):
        self._last_payload = payload
        with self._listeners_lock:
            listeners = list(self._listeners.values())
        for item in listeners:
            loop: asyncio.AbstractEventLoop = item["loop"]
            queue: asyncio.Queue = item["queue"]
            loop.call_soon_threadsafe(queue.put_nowait, payload)

    # ------------ task control ------------
    def _resolve_model(self, name: str) -> Path:
        candidate = (CONFIG.MODEL_FOLDER / name).resolve()
        if not candidate.is_file():
            raise HTTPException(status_code=400, detail=f"model not found: {name}")
        return candidate

    def _resolve_dir(self, raw: str, label: str, must_exist: bool = False) -> Path:
        if not raw:
            raise HTTPException(status_code=400, detail=f"{label} 不能为空")
        path = Path(raw).expanduser().resolve()
        if must_exist and not path.is_dir():
            raise HTTPException(status_code=400, detail=f"{label}文件夹不存在: {raw}")
        if not must_exist:
            path.mkdir(parents=True, exist_ok=True)
        return path

    def start_job(self, payload: dict):
        with self._job_lock:
            if self._current_job and self._current_job.running:
                raise HTTPException(status_code=400, detail="已有算法测试任务在执行")

            model_name = payload.get("model")
            target = payload.get("target")
            output = payload.get("output")
            if not model_name:
                raise HTTPException(status_code=400, detail="model 必填")
            if not target:
                raise HTTPException(status_code=400, detail="target 必填")
            if not output:
                raise HTTPException(status_code=400, detail="output 必填")
            threshold = float(payload.get("threshold", 0.4))
            threshold = max(0.01, min(0.99, threshold))
            mode = payload.get("mode", "copy")
            options = payload.get("options") or {}

            model_path = self._resolve_model(model_name)
            target_path = self._resolve_dir(target, "目标", must_exist=True)
            output_path = self._resolve_dir(output, "输出")

            job = AlgTestJob(
                id=uuid.uuid4().hex,
                model_path=model_path,
                target=target_path,
                output=output_path,
                threshold=threshold,
                mode=mode,
                options={
                    "classify_save": bool(options.get("classify_save", True)),
                    "save_label": bool(options.get("save_label", False)),
                    "prioritize": bool(options.get("prioritize", False)),
                },
                manager=self,
            )
            self._current_job = job
            thread = Thread(target=self._run_job, args=(job,), daemon=True)
            thread.start()
            self._broadcast(job.build_payload("任务已启动"))
            return {"ok": True, "task_id": job.id}

    def stop_job(self, task_id: Optional[str]):
        with self._job_lock:
            job = self._current_job
            if not job or not job.running:
                return {"ok": True, "message": "当前无任务"}
            if task_id and job.id != task_id:
                raise HTTPException(status_code=400, detail="任务 ID 不匹配")
            job.stop_event.set()
            return {"ok": True, "message": "停止指令已发送"}

    def _finish_job(self, job: AlgTestJob, message: str, finished: bool = True):
        job.running = False
        payload = job.build_payload(message, finished=finished)
        self._broadcast(payload)
        with self._job_lock:
            if self._current_job is job:
                self._current_job = None

    # ------------ core job logic ------------
    def _run_job(self, job: AlgTestJob):
        image_paths = _list_image_files(job.target)
        job.total = len(image_paths)
        if not image_paths:
            self._finish_job(job, "未找到可测试图片", finished=True)
            return

        self._broadcast(job.build_payload(f"共 {job.total} 张，准备加载模型"))

        try:
            model = YOLO(str(job.model_path))
        except Exception as exc:
            self._finish_job(job, f"模型加载失败: {exc}", finished=True)
            return

        job.status = "运行中"
        self._broadcast(job.build_payload("模型加载完成，开始遍历图片"))

        for index, image_path in enumerate(image_paths, 1):
            if job.stop_event.is_set():
                job.status = "已停止"
                self._finish_job(job, "任务已停止", finished=True)
                return
            try:
                results = model(str(image_path))
                if not results:
                    raise RuntimeError("模型无返回结果")
                result = results[0]
                boxes = []
                for box in result.boxes:
                    xyxy = box.xyxy[0].cpu().numpy().tolist()
                    label_idx = int(box.cls[0].item())
                    label = result.names.get(label_idx, str(label_idx))
                    boxes.append({
                        "label": label,
                        "conf": float(box.conf[0].item()),
                        "bbox": [float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])]
                    })
                analysis = _analyze_boxes(boxes, job.threshold)
                summary = self._handle_single_image(job, image_path, result, boxes, analysis)
                message = summary.get("message", "")
            except Exception as exc:
                job.errors += 1
                message = f"{image_path.name} 处理失败: {exc}"

            job.processed = index
            payload = job.build_payload(message)
            self._broadcast(payload)

        job.status = "完成"
        self._finish_job(job, f"处理完成，共 {job.total} 张", finished=True)

    def _handle_single_image(self, job: AlgTestJob, image_path: Path, result, boxes: List[dict], analysis: dict):
        combo = analysis["combo"]
        classification = "normal"
        reason = "classified"

        if not analysis["has_boxes"]:
            classification = "normal"
            reason = "empty"
            job.summary["empty"] += 1
        elif analysis["low_conf"]:
            classification = "abnormal"
            reason = "low_confidence"
        elif analysis["overlap_diff"]:
            classification = "abnormal"
            reason = "overlap_diff"
        elif analysis["overlap_same"]:
            classification = "abnormal"
            reason = "overlap_same"

        if classification == "abnormal":
            job.summary["abnormal"] += 1
        else:
            job.summary["normal"] += 1

        if job.priority_mode() and classification == "normal":
            job.summary["skipped"] += 1
            return {"message": f"{image_path.name} 正常 (仅检测)"}

        base_dir = job.output / classification
        sub_dir = {
            "empty": "empty",
            "low_confidence": "low_confidence",
            "overlap_same": "overlap_same",
            "overlap_diff": "overlap_diff",
            "classified": "classified"
        }[reason]

        dest_dir = base_dir / sub_dir
        if job.should_classify() and combo and combo != "empty":
            dest_dir = dest_dir / _sanitize_folder_name(combo)
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = _reserve_path(dest_dir / image_path.name)
        if job.image_mode() == "move":
            shutil.move(str(image_path), dest_path)
        else:
            shutil.copy2(str(image_path), dest_path)

        if job.should_save_label() and boxes:
            if result.masks is not None:
                arr = cv2.imread(str(dest_path))
                wrapper = YoloModelResults(0, 1, arr, result)
                wrapper.threshold = job.threshold
                label_path = _reserve_path(dest_path.with_suffix(".json"))
                label_data = wrapper.to_labelme_json(dest_path)
                label_path.write_text(json.dumps(label_data, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                height, width = result.orig_shape if hasattr(result, "orig_shape") else (0, 0)
                if not width or not height:
                    arr = cv2.imread(str(dest_path))
                    if arr is not None:
                        height, width = arr.shape[:2]
                label_path = _reserve_path(dest_path.with_suffix(".xml"))
                _save_pascal_voc_xml(label_path, dest_path.name, width, height, boxes)

        categories_text = combo if combo else "none"
        message = f"{image_path.name} -> {classification}/{sub_dir} [{categories_text}]"
        return {"message": message}


alg_test_manager = AlgTestManager()
