import logging

import cv2
import numpy as np

from Configs.CameraManageConfig import camera_manage_config


from tool import load_json


def sort_point(shape):
    return shape


def get_trans(data):
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
        print(area_shape)
    assert len(area_shape) == 1 , "area 数量不匹配"
    area_shape = area_shape[0]
    assert len(area_shape) == 4, "area_shape 数量 点 不匹配"
    area_shape = sort_point(area_shape)
    return area_shape


class ConversionImage:
    """
    This class is responsible for converting the image to the desired format.
    """
    def __init__(self, key):
        self.key = key
        calibrate_json_path = camera_manage_config.get_calibrate_json_path(self.key)
        if not calibrate_json_path.exists():
            logging.error(f"{calibrate_json_path} 不存在 ! ")
            json_data = {}
        else:
            json_data = load_json(calibrate_json_path)

        self.trans = get_trans(json_data)

    def image_conversion(self, frame):
        """
        数据转换
        :param frame:
        :return:
        """
        width, height = [512, 512]
        M = cv2.getPerspectiveTransform(self.trans, np.array([(0, 0), (width, 0), (width, height), (0, height)], dtype=np.float32))
        warped = cv2.warpPerspective(frame, M, (width, height))
        return warped