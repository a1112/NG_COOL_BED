from ultralytics import YOLO

import CONFIG

class Result:
    def __init__(self):
        pass

    @property
    def can_get_data(self):
        return False

class SteelDetModel:
    def __init__(self):
        self.model = YOLO(str(CONFIG.MODEL_FOLDER / "steelDet.pt"))   # load a custom model

    def predict(self, image):
        results = self.model(image)
        if results[0].xyxy:
            return results[0].xyxy

    def getSteelRect(self, image):
        results = self.model(image)
        bounding_boxes = []
        for result in results:
            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                label = int(box.cls[0].cpu().numpy())  # 假设类标签是整数
                xmin, ymin, xmax, ymax = xyxy
                bounding_boxes.append((int(xmin), int(ymin), int(xmax-xmin), int(ymax-ymin),label))
        if bounding_boxes:
            max_rect = max(bounding_boxes, key=lambda x: x[2]*x[3])
            return max_rect
        return []


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

