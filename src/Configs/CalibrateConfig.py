from pathlib import Path

import numpy as np
from PIL import Image
import cv2

from Configs.DebugFolderConfig import DebugFolderConfig
from CONFIG import debug_control


def split_image_horizontally(img, num_parts = 4):
    # 获取图像尺寸
    height, width = img.shape[:2]
    # 计算每部分的高度
    part_width = width // num_parts
    # 存储分割后的图像
    parts = []
    for i in range(num_parts):
        # 计算每部分的起始和结束y坐标
        start_x = i * part_width
        end_x = (i + 1) * part_width if i < num_parts - 1 else width
        # 提取图像部分
        part = img[:,start_x :end_x]
        parts.append(part)
    return parts

class CalibrateConfig:
    def __init__(self, image_list):
        self.image_list = image_list
        self.image_ = np.hstack(image_list)
        self.mask_image = None

    @property
    def image(self):
        return self.image_



    @property
    def sub_images(self):
        image_list = self.image_list
        if len(self.image_list) == 1:
            image_list = split_image_horizontally(self.image_list[0])
        # print(f"sub_images {[i.shape for i in image_list]}")
        return image_list


class DebugCalibrateConfig:
    def __init__(self,key):
        self.key = key
        self.testFolder = Path(DebugFolderConfig.FOLDER_MAP[key])
        self.image_list= list(self.testFolder.glob('*.jpg'))
        self.conversion_image_list = None
        self.image_ = None
        self.mask_image_ = None

    def set_image_by_index(self,index):
        url =  self.image_list[index]
        self.image_=np.array(Image.open(url).convert('RGB'))

    @property
    def image(self):
        self.set_image_by_index(debug_control.debug_test_index)
        return self.image_

    @property
    def sub_images(self):
        return split_image_horizontally(self.image)

    @property
    def mask_image(self):
        if self.mask_image_ is None:
            self.mask_image_ = np.zeros_like(self.image)
        return self.mask_image_

    @mask_image.setter
    def mask_image(self, mask_image):
        self.mask_image_ = mask_image