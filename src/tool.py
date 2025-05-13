import json
import datetime

import cv2

import CONFIG
import xml.etree.ElementTree as ET


def load_json(url):
    with open(url, "r", encoding = CONFIG.encoding ) as f:
        return json.load(f)

def load_xml(url):
    in_file = open(url, encoding='utf-8')
    tree = ET.parse(in_file)
    root = tree.getroot()
    objects = root.findall("object")
    re_dict={}
    for obj in objects:
        cls = obj.find('name').text
        xmlbox = obj.find('bndbox')
        b = [int(xmlbox.find('xmin').text),int(xmlbox.find('ymin').text), int(xmlbox.find('xmax').text),
             int(xmlbox.find('ymax').text)]
        re_dict[cls] = b
    return re_dict

def zh_ch(string):
    return string.encode('gbk').decode(errors='ignore')


def show_cv2(img,title="image",rec_list=None):
    cv2.namedWindow(title, flags=cv2.WINDOW_NORMAL)

    if rec_list is not None:
        for item in rec_list:
            x,y,w,h,*_ = list(item)
            name="name"
            color = (0, 255, 0)  # 绿色
            thickness = 5
            # 绘制矩形框
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            # 绘制文本标签
            cv2.putText(img, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness)
    cv2.imshow(zh_ch(title), img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        return

def get_new_data_str():
    return datetime.datetime.now().strftime(CONFIG.DATA_FMT)
def get_now_data_time_str():
    return datetime.datetime.now().strftime(CONFIG.DATETIME_FMT)
