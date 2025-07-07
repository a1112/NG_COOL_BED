import numpy as np

import cv2

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
        self.mask_image=None

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