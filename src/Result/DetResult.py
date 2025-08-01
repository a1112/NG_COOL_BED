import time
from typing import List

import cv2
import numpy as np

import tool
from Configs.CalibrateConfig import CalibrateConfig
from Configs.MappingConfig import MappingConfig
from Result import SteelItem
from Result.SteelItem import SteelItemList, SteelItemSeg
from alg.YoloModelResults import YoloModelResults


def format_mm(mm):
    return round((int(mm) / 1000), 2)

class ResultBase:
    pass


class DetResult(ResultBase):
    """
    单独的 单帧检出数据
    ?  需要怎加 seg


    """
    def __init__(self, calibrate:CalibrateConfig, rec_list, map_config):

        self.calibrate = calibrate
        self.rec_list = rec_list
        self.image = np.copy(calibrate.image)
        self.time=time.time()
        self.map_config:MappingConfig = map_config
        self.obj_list = [SteelItem(rec, self.map_config) for rec in rec_list]
        self.steel_list = [obj for obj in self.obj_list if obj.is_steel]
        self.t_car_list = [obj for obj in self.obj_list if obj.is_t_car]


        self.steel_list.sort(key=lambda steel: steel.name)

    @property
    def steel_infos(self):
        return [obj.dict for obj in self.steel_list]

    @property
    def t_car_infos(self):
        return [obj.dict for obj in self.t_car_list]

    @property
    def infos(self):
        return [obj.dict for obj in self.obj_list]

    @property
    def can_get_data(self):
        for t_car in self.t_car_list:
            t_car: SteelItem
            if t_car.h_mm > self.map_config.MAX_T_CAR_HEIGHT or ( t_car.w_mm > self.map_config.MAX_T_CAR_WIDTH) :
                return False
        return True

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
        thickness = 3
        # 绘制矩形框
        line_p = (int(x + w/2), y+h), (int(x + w/2), self.map_config.down[1])
        cv2.line(self.image, line_p[0], line_p[1] ,(0,255,0), thickness)
        # 绘制文本标签
        cv2.putText(self.image, text, (line_p[0][0],int((line_p[0][1] + line_p[1][1])/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness)

    def get_under_steel(self,in_roll=False, in_cool_bed=False, in_left=False,in_right=False):
        steels = self.steel_list

        if in_roll:
            steels = [steel for steel in steels if steel.in_roll]

        if in_cool_bed:
            steels = [steel for steel in steels if steel.in_cool_bed]

        if in_left:
            steels = [steel for steel in steels if steel.in_left]

        if in_right:
            steels = [steel for steel in steels if steel.in_right]

        if not steels:
            # print(fr"get_under_steel in_roll:{in_roll} in_cool_bed {in_cool_bed} {in_left} {in_right} ")
            # print(self.steel_list)
            # raise
            return SteelItemList(self.map_config, [])

        re_list = []
        base_steel = steels[0]
        for steel in steels:
            steel:SteelItem
            if steel.bottom_mm-base_steel.bottom_mm < self.map_config.MAX_LEN:
                re_list.append(steel)
            else:
                break
        return SteelItemList(self.map_config, re_list)

    @property
    def left_under_steel(self):
        return self.get_under_steel(in_roll = True, in_cool_bed = True, in_left = True)

    @property
    def right_under_steel(self):
        return self.get_under_steel(in_roll = True, in_cool_bed = True, in_right = True)

    @property
    def left_under_cool_bed_steel(self):
        return self.get_under_steel(in_cool_bed=True, in_left=True)

    @property
    def right_under_cool_bed_steel(self):
        return self.get_under_steel(in_cool_bed=True, in_right=True)

    @property
    def left_under_roll_steel(self):
        return self.get_under_steel(in_roll=True, in_left=True)

    @property
    def right_under_roll_steel(self):
        return self.get_under_steel(in_roll=True, in_right=True)

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
        return [steel for steel in self.steel_list if steel.in_roll]

    @property
    def has_cool_bed_steel(self):
        for steel in self.steel_list:
            if steel.in_cool_bed:
                return True
        return False

    @property
    def cool_bed_steel(self):
        return [steel for steel in self.steel_list if steel.in_cool_bed]

    @property
    def left_cool_bed_steel(self):
        return self.get_under_steel(in_roll=True, in_left=True)

    @property
    def right_cool_bed_steel(self):
        return self.get_under_steel(in_roll=True, in_right=True)

    @property
    def show_image(self):
        self.draw_map()
        self.draw_steel()
        return self.image

    def __repr__(self):
        return f"DetResult(time={self.time}, steel_count={len(self.steel_list)}, {self.steel_list}, t_car_count={len(self.t_car_list)})"

def get_contour(mask):
    binary_mask = cv2.bitwise_and(mask, mask)
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

class SegResult(DetResult):
    def __init__(self, det_result: DetResult, yolo_model_results: List[YoloModelResults]):
        super().__init__(det_result.calibrate, det_result.rec_list, det_result.map_config)
        self.det_result = det_result
        self.yolo_model_results = yolo_model_results
        self.mask_list = [res.mask() for res in self.yolo_model_results]
        self.mask = np.hstack(self.mask_list)

        # 定义一个横向膨胀的结构元素（核）
        horizontal_kernel = np.ones((1, 11), np.uint8)  #

        # 应用膨胀操作
        self.mask = cv2.dilate(self.mask, horizontal_kernel, iterations=3)

        self.contour = get_contour(self.mask)

        self.image = self.det_result.image
        self.map_config:MappingConfig = self.det_result.map_config


        self.calibrate = det_result.calibrate
        self.rec_list = det_result.rec_list
        self.image = np.copy(self.calibrate.image)
        self.time=time.time()
        self.map_config:MappingConfig = det_result.map_config
        self.obj_list = [SteelItemSeg(contour_item, self.map_config) for contour_item in self.contour]

        self.steel_list = [obj for obj in self.obj_list if obj.is_steel]
        self.t_car_list = [obj for obj in self.obj_list if obj.is_t_car]


        self.steel_list.sort(key=lambda steel: steel.name)

    @property
    def draw_image(self):
        return self.mask

class SteelResult:
    pass