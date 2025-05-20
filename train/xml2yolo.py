import os
import socket
import xml.etree.ElementTree as ET
from pathlib import Path


def convert_bbox(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def get_classes(item, classes_map_, only=False):
    for key, value in classes_map_.items():
        if only:
            return key
        if item in value:
            return key
    raise ValueError(item)


def convert_annotation(xml_path, output_path, classes_, only=False):
    if not xml_path.exists():
        open(output_path, 'w', encoding='utf-8')
        return

    in_file = open(xml_path, encoding='utf-8')
    out_file = open(output_path, 'w', encoding='utf-8')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    classes = classes_
    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls in ["cae","t_car"]:
            cls = "car"
        # if cls not in classes:
        #     classes.append(cls)
        #     raise ValueError(cls)
        cls_id = classes.index(cls)
        if only:
            cls_id = 0
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
             float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert_bbox((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
    print(classes)


def process_annotations(xml_folder, yolo_folder, classes_, only=False):
    xml_folder = Path(xml_folder)
    yolo_folder= Path(yolo_folder)
    yolo_folder.mkdir(exist_ok=True,parents=True)

    image_files = [f for f in xml_folder.glob("*.*") if Path(f).suffix.lower() in [".jpg",".jpeg",".png"]]
    for image_file in image_files:
        xml_file = image_file.with_suffix(".xml")
        xml_path = xml_folder/xml_file.name
        yolo_path = yolo_folder/xml_file.with_suffix(".txt").name
        convert_annotation(xml_path, yolo_path, classes_, only=only)
        print(f"Converted {xml_file} to YOLO format.")


# 定义类别（确保这些类别与你的XML文件中的类别一致）
classes_ = ['steel', 'car']

print(socket.gethostname())

xml_folder = Path(r'train/data')
yolo_folder = xml_folder.parent / "txt"
yolo_folder.mkdir(parents=True, exist_ok=True)
process_annotations(xml_folder, yolo_folder, classes_, only=False)
