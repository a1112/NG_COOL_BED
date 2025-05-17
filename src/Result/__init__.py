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
        x,y,w,h, self.type_ = self.rec
        self.px_x = x
        self.px_y = y
        self.px_w = w
        self.px_h = h
        self.mm_rec = self.map_config.get_rect(self.rec[:4])

    @property
    def x_mm(self):
        return self.mm_rec[0]

    @property
    def y_mm(self):
        return self.mm_rec[1]

    @property
    def w_mm(self):
        return self.mm_rec[2]

    @property
    def h_mm(self):
        return self.mm_rec[3]

    @property
    def to_roll_mm(self):
        return self.y_mm - self.h_mm

    @property
    def left_mm(self):
        return self.x_mm

    @property
    def right_mm(self):
        return self.x_mm + self.w_mm

    @property
    def top_mm(self):
        return self.y_mm

    @property
    def bottom_mm(self):
        return self.y_mm - self.h_mm

    @property
    def mm_str(self):
        x_mm, y_mm, w_mm, h_mm = self.mm_rec
        return f"x: {format_mm(x_mm)} y: {format_mm(y_mm)} w: {format_mm(w_mm)} h: {format_mm(h_mm)}"

    @property
    def name(self):
        if self.type_ == 0:
            return "steel" +self.mm_str
        return "t_car"

    @property
    def color(self):
        return 200, 0, 0


    @property
    def rect_px(self):
        return self.rec[:4]

    @property
    def in_roll(self):
        return self.bottom_mm < self.map_config.up_seat_d

    @property
    def in_cool_bed(self):
        return self.top_mm >= self.map_config.up_seat_u


class DetResult:
    """
    单独的 单帧检出数据
    """
    def __init__(self,image,rec_list, map_config):
        self.image = np.copy(image)
        self.time=time.time()
        self.map_config:MappingConfig = map_config
        self.rec_list = rec_list
        self.steel_list = [SteelItem(rec, self.map_config) for rec in self.rec_list]

    @property
    def can_get_data(self):
        return False

    def draw_steel_in_roll(self):
        """
        绘制距离
        :return:
        """

    def draw_steel_item(self,steel):
        steel: SteelItem
        x, y, w, h, = steel.rect_px
        name = steel.name
        thickness = 2
        # 绘制矩形框
        cv2.rectangle(self.image, (x, y), (x + w, y + h), steel.color, thickness)
        # 绘制文本标签
        cv2.putText(self.image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness)

    def draw_steel(self):
        if self.steel_list is not None:
            for steel in self.steel_list:
                steel : SteelItem
                self.draw_steel_item(steel)
                self.draw_out_line(steel)


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

    def draw_out_line(self, steel):
        steel: SteelItem
        x, y, w, h, = steel.rect_px
        text = f": {format_mm(steel.to_roll_mm)} m "
        thickness = 2
        # 绘制矩形框
        line_p = (int(x + w/2), y+h), (int(x + w/2), self.map_config.down[1])
        cv2.line(self.image, line_p[0], line_p[1] ,(0,255,0), thickness)
        # 绘制文本标签
        cv2.putText(self.image, text, (line_p[0][0],int((line_p[0][1] + line_p[1][1])/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness)

    @property
    def has_roll_steel(self):
        """
         辊道是否存在
        """
        for steel in self.steel_list:
            if steel.in_roll:
                return True
        return False

    @property
    def roll_steel(self):
        re_list=[]
        for steel in self.steel_list:
            if steel.in_roll:
                re_list.append(steel)
        return re_list

    @property
    def has_cool_bed_steel(self):
        for steel in self.steel_list:
            if steel.in_cool_bed:
                return True
        return False

    @property
    def cool_bed_steel(self):
        re_list=[]
        for steel in self.steel_list:
            if steel.in_cool_bed:
                re_list.append(steel)
        return re_list

    @property
    def show_image(self):
        self.draw_map()
        self.draw_steel()
        return self.image


def format_mm(mm):
    return round((int(mm) / 1000), 2)
