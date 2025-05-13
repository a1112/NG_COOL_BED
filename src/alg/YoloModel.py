import cv2
import numpy as np
from ultralytics import YOLO

import CONFIG


class SteelDetModel:
    def __init__(self):
        self.model = YOLO(str(CONFIG.MODEL_FOLDER / "steelDet.pt"))   # load a custom model

    def predict(self, image):
        results = self.model(image)
        if results[0].xyxy:
            return results[0].xyxy

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
        self.model = YOLO(str(CONFIG.base_config_folder / "model/CoilSeg.pt"))   # load a custom model

    def predict(self, image):
        results = self.model(image)
        if results[0].masks:
            orig_shape = results[0].masks.orig_shape
            mask = results[0].masks.data[0].cpu().numpy()*255
            mask = mask.astype(np.uint8)
            mask = cv2.resize(mask, orig_shape)
            return mask

        return np.zeros_like(image)

