import json
import datetime
import time

import cv2

import CONFIG
import xml.etree.ElementTree as ET
from queue import Queue

from threading import Thread

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
        x,y,x2,y2 = b
        re_dict[cls] = [x, y, x2-x, y2-y]
    return re_dict

def zh_ch(string):
    return string.encode('gbk').decode(errors='ignore')


class ShowThread(Thread):
    def __init__(self):
        super().__init__()
        self.image_show_queue = Queue()
        self.start()

    def run(self):
        while True:
            title,img = self.image_show_queue.get()
            cv2.namedWindow(title, flags=cv2.WINDOW_NORMAL)
            cv2.imshow(zh_ch(title), img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return
            time.sleep(0.01)

    def add(self,title,img):
        self.image_show_queue.put([title, img])


show_thread=ShowThread()
def show_cv2(img,title="image"):
    """避免多线程显示失败"""
    return show_thread.add(title,img)



def get_new_data_str():
    return datetime.datetime.now().strftime(CONFIG.DATA_FMT)
def get_now_data_time_str():
    return datetime.datetime.now().strftime(CONFIG.DATETIME_FMT)
