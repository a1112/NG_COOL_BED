import logging

import cv2
import numpy as np

from CONFIG import CalibratePath
from tool import load_json


def sort_point(points, key):
    # 按 y 坐标升序排列

    print(fr"sort_point key {key}")

    if key=="L2_7":
        sorted_by_x = sorted(points, key=lambda p: p[0])

        # 分离顶部和底部点
        r_two = sorted_by_x[:2]
        l_two = sorted_by_x[2:]

        # 顶部按 x 升序排列 → 左上、右上
        top_sorted = sorted(r_two, key=lambda p: p[1])

        # 底部按 x 降序排列 → 右下、左下
        bottom_sorted = sorted(l_two, key=lambda p: -p[1])

        # 合并结果
        ordered_points =  top_sorted + bottom_sorted

    else:
        sorted_by_y = sorted(points, key=lambda p: p[1])

        # 分离顶部和底部点
        top_two = sorted_by_y[:2]
        bottom_two = sorted_by_y[2:]

        # 顶部按 x 升序排列 → 左上、右上
        top_sorted = sorted(top_two, key=lambda p: p[0])

        # 底部按 x 降序排列 → 右下、左下
        bottom_sorted = sorted(bottom_two, key=lambda p: -p[0])

        # 合并结果
        ordered_points = top_sorted + bottom_sorted

    return ordered_points

def get_trans(data, key):
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
    area_shape = sort_point(area_shape, key)
    return area_shape


def get_calibrate_json_path(key):
    file_name = key + ".json"
    return CalibratePath / file_name

class ConversionImage:
    """
    This class is responsible for converting the image to the desired format.
    """
    def __init__(self, key,width, height ):
        self.key = key
        calibrate_json_path = get_calibrate_json_path(self.key)
        # self.map = camera_manage_config.get_map(self.key)

        if not calibrate_json_path.exists():
            logging.error(f"{calibrate_json_path} 不存在 ! ")
            json_data = {}
        else:
            json_data = load_json(calibrate_json_path)
        self.width = width
        self.height = height
        self.trans = np.array(get_trans(json_data,key), np.float32)
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