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
        if cls == "cae":
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
    if not os.path.exists(yolo_folder):
        os.makedirs(yolo_folder)

    xml_files = [f for f in os.listdir(xml_folder) if f.endswith('.xml')]

    for xml_file in xml_files:
        xml_path = os.path.join(xml_folder, xml_file)
        yolo_path = os.path.join(yolo_folder, xml_file.replace('.xml', '.txt'))
        convert_annotation(xml_path, yolo_path, classes_, only=only)
        print(f"Converted {xml_file} to YOLO format.")


# 定义类别（确保这些类别与你的XML文件中的类别一致）
classes_ = ['steel', 'car']

print(socket.gethostname())

xml_folder = Path(r'train/data')
yolo_folder = xml_folder.parent / "txt"
yolo_folder.mkdir(parents=True, exist_ok=True)
process_annotations(xml_folder, yolo_folder, classes_, only=True)
