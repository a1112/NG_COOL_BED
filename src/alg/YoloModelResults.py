from pathlib import Path

import cv2
import numpy as np
from ultralytics.engine.results import Results
from PIL import Image

import tool
from Configs.ClassConfig import name_to_color


class YoloModelResultsBase:
    def __init__(self, image, result):
        self.result:Results = result
        if isinstance(image, str):
            self.image = cv2.imread(image)
        if isinstance(image, Image.Image):
            self.image = np.array(image)
        else:
            self.image = image
        self.image: np.ndarray
        self.threshold = 0.4

    @property
    def all_names(self):
        return self.result.names

    @property
    def boxes(self):
        return self.result.boxes



class YoloModelResults(YoloModelResultsBase):
    def __init__(self,index,len_, image, result):
        self.index = index
        self.len_ = len_
        super(YoloModelResults, self).__init__(image, result)

    @property
    def contour_by_data(self):
        """
        获取轮廓数据
        :return: 返回轮廓数据列表
        """
        if self.result.masks is None:
            print("No masks found in the result.")
            return []
        contours_list = []
        for i, (box, mask) in enumerate(zip(self.result.boxes, self.result.masks)):
            if box.conf < self.threshold:
                continue
            binary_mask = (mask.data[0].cpu().numpy() > 0.5).astype(np.uint8) * 255
            # 查找轮廓
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            max_contour = max(contours, key=cv2.contourArea)
            # max_area = cv2.contourArea(max_contour)
            # 缩放轮廓点
            scaled_contour = []
            for point in max_contour:
                x, y = point[0]
                scaled_contour.append([[int(x * self.scale_x), int(y * self.scale_y)]])
            contours_list.append(np.array(scaled_contour))

        return contours_list

    @property
    def scale_x(self):
        """
        获取图像的宽度缩放比例
        :return: 返回宽度缩放比例
        """
        return self.image.shape[1] / self.result.masks[0][0].data[0].shape[1]

    @property
    def scale_y(self):
        """
        获取图像的高度缩放比例
        :return: 返回高度缩放比例
        """
        return self.image.shape[0] / self.result.masks[0].data[0].shape[0]


    def contour(self):
        cons = []
        labels = []
        if self.result.masks is None:
            return cons
        for i, (box, mask) in enumerate(zip(self.result.boxes, self.result.masks)):
            if box.conf < self.threshold:
                continue
            label = self.all_names[int(box.cls[0])]
            contours = mask.xy
            # 绘制轮廓（在原图上）
            contour = np.array(contours, dtype=np.float32)  # 保持浮点精度
            contour_int = np.round(contour).astype(np.int32).tolist()
            for point_index, point in enumerate(contour_int[0]):
                if self.index > 0:
                    if point[0] < 20:
                        point[0]=0
                if self.index < len(contour_int) - 1:
                    if point[0]> self.image.shape[1]-20:
                        point[0] =  self.image.shape[1]
            contour_int = np.round(contour_int).astype(np.int32)
            cons.append(contour_int)
            labels.append(label)
        return cons, labels

    def get_draw(self,image=None):
        if image is None:
            image = self.image.copy()
        cv2.drawContours(
            image,
            self.contour(),
            -1,  # 绘制所有轮廓
            (0, 255, 0),  # 绿色
            3  # 线宽
        )
        return image

    def mask(self):
        mask_image = np.zeros(self.image.shape[:2], dtype=np.uint8)
        for cont ,label in zip(*self.contour()):
            if name_to_color(label):
                color = name_to_color(label)
                cv2.drawContours(mask_image, cont, -1, color, -1)
        return mask_image

    def get_mask(self):
        """
        获取掩码
        """
        pass
        # mask = self.result.masks.data.cpu().numpy()
        # mask = np.sum(mask, axis=0)
        # mask = np.squeeze(mask)
        # mask = (mask * 255).astype(np.uint8)
        # mask=cv2.resize(mask,(self.image.shape[1],self.image.shape[0]))
        # return mask


    def show(self):
        """
         opencv 显示轮廓
        """
        draw_image = self.get_draw()
        tool.show_cv2(draw_image,title = f"Object Contours")

    def to_labelme_json(self,file_path):
        """
        Convert the segmentation results to a labelme format.
        """
        self.image: np.ndarray
        labelme_data = {
            "version": "4.5.13",
            "flags": {},
            "shapes": [],
            "imagePath": Path(file_path).with_suffix(".jpg").name,
            "imageData": None,
            "imageHeight": self.image.shape[0],
            "imageWidth": self.image.shape[1]
        }
        if self.result.masks is None:
            print("No masks found in the result.")
            return labelme_data

        for i, (box, mask) in enumerate(zip(self.result.boxes, self.result.masks)):

            contours = mask.xy
            if box.conf<self.threshold:
                continue

            contour = np.array(contours, dtype=np.float32)
            contour_int = np.round(contour).astype(np.int32).tolist()
            labelme_data["shapes"].append({
                "label": self.all_names[int(box.cls[0])],
                "points": contour_int[0],
                "group_id": None,
                "shape_type": "polygon",
                "flags": {}
            })
        return labelme_data

    def save_json(self, file_path):
        """
        Save the labelme format to a JSON file.
        """
        import json
        labelme_data = self.to_labelme_json(file_path)
        with open(file_path, 'w') as f:
            json.dump(labelme_data, f, indent=4)

    def save_xml(self, file_path):
        """
        Save the segmentation results to an XML file.
        """
        import xml.etree.ElementTree as ET

        root = ET.Element("annotation")
        ET.SubElement(root, "filename").text = Path(file_path).with_suffix(".jpg").name
        ET.SubElement(root, "size").text = f"{self.image.shape[1]} {self.image.shape[0]}"

        if self.result.masks is None:
            print("No masks found in the result.")
            return

        for i, (box, mask) in enumerate(zip(self.result.boxes, self.result.masks)):
            contours = mask.xy
            contour = np.array(contours, dtype=np.float32)
            contour_int = np.round(contour).astype(np.int32).tolist()
            obj = ET.SubElement(root, "object")
            ET.SubElement(obj, "name").text = self.all_names[int(box.cls[0])]
            polygon = ET.SubElement(obj, "polygon")
            for point in contour_int[0]:
                ET.SubElement(polygon, "pt").text = f"{point[0]} {point[1]}"

        tree = ET.ElementTree(root)
        tree.write(file_path)