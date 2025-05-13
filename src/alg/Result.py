import cv2
import numpy as np

from Configs.MappingConfig import MappingConfig


class DetResult:
    def __init__(self,image,rec_list, map_config):
        self.image = np.copy(image)
        self.map_config:MappingConfig = map_config
        self.rec_list = rec_list

    @property
    def can_get_data(self):
        return False

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
        cv2.rectangle(self.image, (x, y), (x2, y2), (100, 50, 0), 5)

    @property
    def show_image(self):
        self.draw_steel()
        self.draw_map()
        return self.image