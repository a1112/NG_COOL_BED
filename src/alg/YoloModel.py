from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import CONFIG
from alg.YoloModelResults import YoloModelDetResults, YoloModelSegResults

def get_image(url_):
    return Image.open(url_)


class SteelDetModel:
    def __init__(self):
        self.model = YOLO(str(CONFIG.MODEL_FOLDER / "steelDet.pt"))   # load a custom model

    def predict(self, image):
        results = self.model(image)
        if results[0].xyxy:
            return results[0].xyxy
        return None

    def get_steel_rect(self, image):
        results = self.model(image)
        bounding_boxes = []
        for result in results:
            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                label = int(box.cls[0].cpu().numpy())  # 假设类标签是整数
                xmin, ymin, xmax, ymax = xyxy
                bounding_boxes.append([int(xmin), int(ymin), int(xmax-xmin), int(ymax-ymin),label])
        return bounding_boxes


class SteelSegModel:
    def __init__(self):
        self.model = YOLO(str(CONFIG.MODEL_FOLDER / "steelSeg.pt"))   # load a custom model

    def predict(self, image):
        results = self.model(image)
        res_data = YoloModelSegResults(image,results[0])
        return res_data



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
    ssm = SteelSegModel()

    folder =Path(__file__).parent.parent.parent/"test"/"seg"
    print(folder)
    for f_ in folder.glob("*.png"):
        text_image_ = get_image(f_)
        test_one_image(ssm, text_image_).show()
        # input()