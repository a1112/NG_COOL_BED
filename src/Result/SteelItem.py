from typing import List

import cv2
import numpy as np

from Configs.ClassConfig import id_to_name
from Configs.MappingConfig import MappingConfig


def format_mm(mm):
    return round((int(mm) / 1000), 2)




class SteelItemBase:
    def __init__(self, map_config: MappingConfig):
        self.map_config = map_config


class SteelItem(SteelItemBase):
    """
    单独的 item
    """
    def __init__(self, rec, map_config):
        super().__init__(map_config)
        self.rec=rec
        x,y,w,h, self.type_ = self.rec
        self.px_x = x
        self.px_y = y
        self.px_w = w
        self.px_h = h
        self.mm_rec = self.map_config.get_rect(self.rec[:4])

    @property
    def name(self):
        return id_to_name(self.type_)

    @property
    def is_steel(self):
        return self.name == "steel"

    @property
    def is_t_car(self):
        return self.name in ["t_car", "d_car" ]

    @property
    def x_mm(self):
        return self.mm_rec[0]

    @property
    def x2_mm(self):
        return self.x_mm+self.w_mm

    @property
    def y_mm(self):
        return self.mm_rec[1]

    @property
    def y2_mm(self):
        return self.y_mm-self.h_mm

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


    @property
    def in_left(self):
        return self.x_mm < self.map_config.mm_center_x-100

    @property
    def in_right(self):
        return self.x_mm+self.w_mm > self.map_config.mm_center_x-100

    @property
    def to_roll_center_y(self):
        # 距离中心线的建立
        return (self.y2_mm+ self.h_mm/2) - self.map_config.roll_center_y

    @property
    def rotated(self):
        return 0

    @property
    def dict(self):
        return {
            "x_px":self.rec[0],
            "y_px": self.rec[1],
            "w_px": self.rec[2],
            "h_px": self.rec[3],
            "x_mm": self.mm_rec[0],
            "y_mm": self.mm_rec[1],
            "w_mm": self.mm_rec[2],
            "h_mm": self.mm_rec[3],
            "name": self.name,
            "in_left": self.in_left,
            "in_right": self.in_right,
            "in_cool_bed": self.in_cool_bed,
            "in_roll": self.in_roll,
            "to_roll_center_y": self.to_roll_center_y,
            "rotated": round(self.rotated,2),
        }

    def __repr__(self):
        return fr"SteelItem {self.name} {self.rec} {self.mm_rec}"

def contour_to_rec(contour_item):
    x_mm, y_mm, x_max, y_max = None, None, None,None
    for point in contour_item:
        x,y=point[0]
        if x_mm is None:
            x_mm=x
        if y_mm is None:
            y_mm=y
        if x_max is None:
            x_max=x
        if y_max is None:
            y_max=y
        if x_mm > x:
            x_mm=x
        if y_mm > y:
            y_mm = y
        if x_max < x:
            x_max = x
        if y_max < y:
            y_max = y
    return [int(x_mm), int(y_mm), int(x_max-x_mm), int(y_max-y_mm)]

def get_box(contour_list):

    for contour in contour_list:
        rec = contour_to_rec(contour)

def format_rotate(rotate_):
    if rotate_ < 45:
        return rotate_
    return format_rotate(rotate_ - 90)

class SteelItemSeg(SteelItem):
    def __init__(self, contour, map_config):
        self.rec = contour_to_rec(contour)+[0]
        self.rotated_rect = cv2.minAreaRect(contour)
        # 提取四个顶点坐标
        box_points = cv2.boxPoints(self.rotated_rect)
        box_points = np.int8(box_points)
        self.rotated_ = format_rotate(self.rotated_rect[-1] )
        # print(fr"self.rotated_ {self.rotated_} box_points: {box_points}")

        # print(fr"self.rec {self.rec}")
        super().__init__(self.rec, map_config)

    @property
    def rotated(self):
        return self.rotated_

    def __repr__(self):
        return fr"SteelItemSeg {self.rotated_rect} {self.name} {self.rec} {self.mm_rec}"

class SteelItemList(SteelItemBase):
    def __init__(self, map_config, steels: List[SteelItem]):
        super().__init__(map_config)
        self.steels = steels
        self.has_steel =  bool(len(steels))

    @property
    def x_mm(self):
        if self.has_steel:
            left = self.steels[0].x_mm
            for steel in self.steels:
                if steel.x_mm<=left:
                    left = steel.x_mm
            return left
        return 0

    @property
    def x2_mm(self):
        if self.has_steel:
            right = self.steels[0].x2_mm
            for steel in self.steels:
                if steel.x2_mm>= right:
                    right = steel.x2_mm
            return right
        return 0

    @property
    def y_mm(self):
        if self.has_steel:
            top = self.steels[0].y_mm
            for steel in self.steels:
                if steel.y_mm >= top:
                    top = steel.y_mm
            return top
        return 0

    @property
    def to_under_mm(self):
        if self.y_mm==0 and self.h_mm==0:
            return self.map_config.to_up_seat_height
        return int(self.y_mm-self.h_mm - self.map_config.to_up_seat_height)

    @property
    def rol_to_center(self):
        if self.y_mm==0 and self.h_mm==0:
            return 0
        return  int(self.y_mm-self.h_mm/2 - self.map_config.roll_center_y )


    @property
    def y2_mm(self):
        if self.has_steel:
            btn = self.steels[0].y2_mm
            for steel in self.steels:
                if steel.y2_mm <= btn:
                    btn = steel.y2_mm
            return btn
        return 0

    @property
    def w_mm(self):
        return self.x2_mm-self.x_mm

    @property
    def h_mm(self):
        return self.y_mm-self.y2_mm

    @property
    def to_roll_center_y(self):
        # 距离中心线的建立
        if self.y_mm==0 and self.h_mm==0:
            return 0
        return (self.y2_mm+ self.h_mm/2) - self.map_config.roll_center_y

    @property
    def rotated(self):
        print(fr"SteelItemList get rotated: {self.steels}")
        res = 0
        for steel in self.steels:
            if abs(steel.rotated) > abs(res):
                res = steel.rotated
        return res

    def __repr__(self):
        return fr"SteelItemList {self.steels}"

class SteelItemNone:
    """
    没有钢卷的情况
    """
    def __init__(self):
        pass

    @property
    def has_steel(self):
        return False

    @property
    def x_mm(self):
        return 0

    @property
    def y_mm(self):
        return 0

    @property
    def to_under_mm(self):
        return 0

    @property
    def rol_to_center(self):
        return 0

    @property
    def w_mm(self):
        return 0

    @property
    def h_mm(self):
        return 0

    @property
    def to_roll_center_y(self):
        return 0

    @property
    def rotated(self):
        return 0

    def __repr__(self):
        return fr"SteelItemNone"