import logging
import json
from pathlib import Path

import cv2
import numpy as np

from CONFIG import CalibratePath
from tool import load_json


def _apply_custom_order(points, order_labels):
    """
    根据自定义标注顺序重排为 [tl, tr, br, bl]。
    支持别名：tl/lt、tr/rt、br/rb、bl/lb。
    """
    alias = {"lt": "tl", "rt": "tr", "rb": "br", "lb": "bl"}
    norm = [alias.get(label.lower(), label.lower()) for label in order_labels]
    idx_map = {label: i for i, label in enumerate(norm)}
    required = ["tl", "tr", "br", "bl"]
    for req in required:
        if req not in idx_map:
            raise ValueError(f"custom order missing label: {req}")
    return [
        points[idx_map["tl"]],
        points[idx_map["tr"]],
        points[idx_map["br"]],
        points[idx_map["bl"]],
    ]


def sort_point(points, key, order_labels=None):
    print(fr"sort_point key {key}")

    if order_labels:
        try:
            return _apply_custom_order(points, order_labels)
        except Exception as exc:  # noqa: BLE001
            logging.error(f"{key}: 自定义顺序解析失败 {order_labels}: {exc}")

    # 通用排序规则：按 y 分上下，再按 x 分左右
    sorted_by_y = sorted(points, key=lambda p: p[1])

    # 分离顶部和底部点
    top_two = sorted_by_y[:2]
    bottom_two = sorted_by_y[2:]

    # 顶部按 x 升序排列 → 左上、右上
    top_sorted = sorted(top_two, key=lambda p: p[0])

    # 底部按 x 降序排列 → 右下、左下
    bottom_sorted = sorted(bottom_two, key=lambda p: -p[0])

    # 合并结果：左上、右上、右下、左下
    ordered_points = top_sorted + bottom_sorted

    return ordered_points

def get_trans(data, key, order_labels=None):
    """
    获取数据
    :param data:
    :return:
    """
    shapes=data["shapes"]
    area_shape = []
    for shape in shapes:
        if shape["label"].lower() == "area":
            area_shape.append( shape["points"]  )
    assert len(area_shape) == 1 , "area 数量不匹配"
    area_shape = area_shape[0]
    assert len(area_shape) == 4, "area_shape 数量 点 不匹配"
    area_shape = sort_point(area_shape, key, order_labels)
    return area_shape


def get_calibrate_json_path(key, calibrate_root: Path = CalibratePath):
    file_name = key + ".json"
    return calibrate_root / file_name


def load_camera_order(calibrate_root: Path, key: str):
    manage_path = calibrate_root / "CameraManage.json"
    if not manage_path.is_file():
        return None
    try:
        data = json.loads(manage_path.read_text(encoding="utf-8"))
        # 1) 顶层 camera_order
        order_map = data.get("camera_order") or {}
        order_labels = order_map.get(key)
        if order_labels and len(order_labels) == 4:
            return order_labels
        # 2) 按前缀匹配 group 下的 camera_order
        prefix = key.split("_", 1)[0] if "_" in key else key
        group_cfg = (data.get("group") or {}).get(prefix) or {}
        order_map = group_cfg.get("camera_order") or {}
        order_labels = order_map.get(key)
        if order_labels and len(order_labels) == 4:
            return order_labels
    except Exception:
        return None
    return None

class ConversionImage:
    """
    This class is responsible for converting the image to the desired format.
    """
    def __init__(self, key,width, height, calibrate_root: Path = CalibratePath ):
        self.key = key
        self.calibrate_root = calibrate_root
        self.order_labels = load_camera_order(self.calibrate_root, self.key)
        calibrate_json_path = get_calibrate_json_path(self.key, self.calibrate_root)
        # self.map = camera_manage_config.get_map(self.key)

        if not calibrate_json_path.exists():
            logging.error(f"{calibrate_json_path} 不存在 ! ")
            json_data = {}
        else:
            json_data = load_json(calibrate_json_path)
        self.width = width
        self.height = height
        self.trans = np.array(get_trans(json_data,key, self.order_labels), np.float32)
        if key=="L2_7":
            pass
            # print(json_data)
            # print(self.order_labels)
            # print(self.trans)
        self.M = cv2.getPerspectiveTransform(self.trans, np.array([(0, 0), (width, 0), (width, height), (0, height)], dtype=np.float32))

    def __call__(self, *args, **kwargs):
        frame = args[0]
        return self.image_conversion(frame)

    def image_conversion(self, frame):
        """
        数据转换
        :param frame:
        :return:
        """
        warped = cv2.warpPerspective(frame, self.M, (self.width, self.height))
        return warped
