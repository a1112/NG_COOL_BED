import time

import cv2
import numpy as np

from Configs.MappingConfig import MappingConfig


class SteelItem:
    """
    单独的 item
    """
    def __init__(self,rec,map_config):
        self.rec=rec
        self.map_config:MappingConfig = map_config
        x,y,w,h = self.rec
        self.px_x = x
        self.px_y = y
        self.px_w = w
        self.px_h = h
        mm_rec = self.map_config.get_rect(self.rec)

class DetResult:
    def __init__(self,image,rec_list, map_config):
        self.image = np.copy(image)
        self.time=time.time()
        self.map_config:MappingConfig = map_config
        self.rec_list = rec_list
        self.steel_list = [SteelItem(rec, self.map_config)for rec in self.rec_list]

    @property
    def can_get_data(self):
        return False

    def draw_steel_in_roll(self):
        """
        绘制距离
        :return:
        """

    def draw_steel(self):
        if self.rec_list is not None:
            for item in self.rec_list:
                x, y, w, h, *_ = list(item)
                name = "steel"
                thickness = 2
                # 绘制矩形框
                cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 255, 0) , thickness)
                # 绘制文本标签
                cv2.putText(self.image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness)


    def draw_map(self):
        up_rect = self.map_config.up
        x,y,x2,y2 = up_rect
        cv2.rectangle(self.image, (x, y), (x2, y2), (100, 50, 0), 3)

        down_rect = self.map_config.down
        x, y, x2, y2 = down_rect
        cv2.rectangle(self.image, (x, y), (x2, y2), (0, 50, 100), 3)

        cool_bed_rect = self.map_config.cool_bed
        x, y, x2, y2 = cool_bed_rect
        cv2.rectangle(self.image, (x, y), (x2, y2), (0, 100, 100), 3)


    @property
    def show_image(self):
        self.draw_steel()
        self.draw_map()

        return self.image