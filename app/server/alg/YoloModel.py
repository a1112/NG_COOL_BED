from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import CONFIG
from Configs.CalibrateConfig import CalibrateConfig
from Configs.GroupConfig import GroupConfig
from Result.DetResult import DetResult, SegResult
from alg.YoloModelResults import YoloModelResults
from tool import show_cv2


def get_image(url_):
    return Image.open(url_)


class SteelDetModel:
    def __init__(self):
        self.model = YOLO(str(CONFIG.MODEL_FOLDER / "steelDet.pt"))   # load a custom model

    def predict(self, image):
        results = self.model(image, device=CONFIG.YOLO_DEVICE)
        if results[0].xyxy:
            return results[0].xyxy
        return None

    def get_steel_rect(self, image):
        results = self.model(image, device=CONFIG.YOLO_DEVICE)
        bounding_boxes = []
        for result in results:
            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                label = int(box.cls[0].cpu().numpy())  # 假设类标签是整数
                xmin, ymin, xmax, ymax = xyxy
                bounding_boxes.append([int(xmin), int(ymin), int(xmax-xmin), int(ymax-ymin),label])
        return bounding_boxes


class SteelAreaSegModel:
    def __init__(self):
        self.model = YOLO(str(CONFIG.MODEL_FOLDER / "steelSeg.pt"))   # load a custom model

    def predict(self, image_list):
        results = self.model(image_list, device=CONFIG.YOLO_DEVICE)
        len_= len(image_list)
        res_data = [YoloModelResults(index,len_,image, result) for index, image, result in zip(range(len_), image_list, results)]
        return res_data


class SteelPredict:
    def __init__(self):
        self.det_model = SteelDetModel()
        self.seg_model = SteelAreaSegModel()

    def predict(self,calibrate:CalibrateConfig, group_config:GroupConfig):
        model_data = self.det_model.get_steel_rect(calibrate.image)
        steel_info = DetResult(calibrate, model_data, group_config.map_config)

        if CONFIG.SHOW_STEEL_PREDICT:
            show_cv2(steel_info.show_image, title=fr"j_{group_config.key}_" + group_config.msg)

        if steel_info.can_get_data and CONFIG.useSegModel:
            steel_info = SegResult(steel_info, self.seg_model.predict(calibrate.sub_images) )
            if CONFIG.SHOW_STEEL_PREDICT:
                show_cv2(steel_info.draw_image, title=fr"j_seg_{group_config.key}_" + group_config.msg)
            calibrate.mask_image = steel_info.mask
        return steel_info

def test_one_image(mask_model,text_image):
    res = mask_model.predict(text_image)
    return res
    # alpha_mask = Image.fromarray(res).convert("RGBA")
    # alpha_mask.putalpha(int(255 * 0.5))
    # alpha_mask = alpha_mask.resize(text_image.size)
    # print(text_image)
    # print(alpha_mask)
    # return Image.alpha_composite(text_image.convert("RGBA"), alpha_mask)



if __name__ =="__main__":
    ssm = SteelAreaSegModel()
    print(ssm)
    folder =Path(__file__).parent.parent.parent/"test"/"seg"
    print(folder)
    for f_ in folder.glob("*.png"):
        text_image_ = get_image(f_)
        test_one_image(ssm, text_image_).show()
        # input()
