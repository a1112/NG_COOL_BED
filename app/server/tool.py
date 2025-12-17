import json
import datetime
import time
from lxml import etree
from pathlib import Path

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
        self._windows = set()
        self.start()

    def run(self):
        while True:
            if not getattr(CONFIG, "SHOW_OPENCV", True):
                try:
                    cv2.destroyAllWindows()
                except Exception:
                    pass
                self._windows.clear()
                time.sleep(0.05)
                continue

            try:
                title, img = self.image_show_queue.get(timeout=0.03)
            except Exception:
                cv2.waitKey(1)
                continue

            window_name = zh_ch(title)
            try:
                if window_name not in self._windows:
                    cv2.namedWindow(window_name, flags=cv2.WINDOW_NORMAL)
                    self._windows.add(window_name)
                cv2.imshow(window_name, img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    try:
                        cv2.destroyWindow(window_name)
                    except Exception:
                        pass
                    self._windows.discard(window_name)
            except Exception:
                try:
                    cv2.destroyWindow(window_name)
                except Exception:
                    pass
                self._windows.discard(window_name)

    def add(self,title,img):
        self.image_show_queue.put([title, img])


show_thread=ShowThread()


class TempSaveThread(Thread):
    def __init__(self):
        super().__init__()
        self.image_save_queue = Queue()
        self.start()

    def run(self):
        while True:
            filename,img = self.image_save_queue.get()
            cv2.imwrite(filename, img)

    def add(self,filename,img):
        self.image_save_queue.put([filename, img])

temp_save_thread=TempSaveThread()

def save_temp(filename,img):
    return temp_save_thread.add(filename,img)

def show_cv2(img,title="image"):
    """避免多线程显示失败"""
    if not getattr(CONFIG, "SHOW_OPENCV", True):
        return
    return show_thread.add(title,img)


def set_show_cv2_enabled(enable: bool):
    """
    Toggle OpenCV display and destroy existing windows when disabling.
    """
    enable = bool(enable)
    CONFIG.SHOW_OPENCV = enable
    if not enable:
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
    return CONFIG.SHOW_OPENCV


def is_show_cv2_enabled():
    return getattr(CONFIG, "SHOW_OPENCV", True)



def get_new_data_str():
    return datetime.datetime.now().strftime(CONFIG.DATA_FMT)
def get_now_data_time_str():
    return datetime.datetime.now().strftime(CONFIG.DATETIME_FMT)

def create_xml(file_name, img_shape, bounding_boxes, output_folder=None):
    annotation = etree.Element("annotation")
    if output_folder is None:
        output_folder = Path(file_name).parent
    folder = etree.SubElement(annotation, "folder")
    folder.text = "images"

    filename = etree.SubElement(annotation, "filename")
    filename.text = str(file_name)

    size = etree.SubElement(annotation, "size")
    width = etree.SubElement(size, "width")
    width.text = str(img_shape[1])
    height = etree.SubElement(size, "height")
    height.text = str(img_shape[0])
    depth = etree.SubElement(size, "depth")
    depth.text = str(img_shape[2])

    for bbox in bounding_boxes:
        xmin, ymin, xmax, ymax, class_id, source, label = bbox
        obj = etree.SubElement(annotation, "object")

        name = etree.SubElement(obj, "name")
        name.text = str(label)

        bndbox = etree.SubElement(obj, "bndbox")
        xmin_elem = etree.SubElement(bndbox, "xmin")
        xmin_elem.text = str(xmin)
        ymin_elem = etree.SubElement(bndbox, "ymin")
        ymin_elem.text = str(ymin)
        xmax_elem = etree.SubElement(bndbox, "xmax")
        xmax_elem.text = str(xmax)
        ymax_elem = etree.SubElement(bndbox, "ymax")
        ymax_elem.text = str(ymax)

    tree = etree.ElementTree(annotation)
    xml_path = Path(output_folder) / Path(file_name).with_suffix('.xml').name
    tree.write(str(xml_path), pretty_print=True, xml_declaration=True, encoding="utf-8")
    print(f"Saved XML to {xml_path}")
