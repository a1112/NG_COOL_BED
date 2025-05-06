import json
import datetime

import cv2

import CONFIG


def load_json(url):
    with open(url, "r", encoding = CONFIG.encoding ) as f:
        return json.load(f)
def zh_ch(string):
    return string.encode('gbk').decode(errors='ignore')


def show_cv2(img,title="image"):
    cv2.namedWindow(title, flags=cv2.WINDOW_NORMAL)
    cv2.imshow(zh_ch(title), img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return

def get_new_data_str():
    return datetime.datetime.now().strftime(CONFIG.DATA_FMT)
def get_now_data_time_str():
    return datetime.datetime.now().strftime(CONFIG.DATETIME_FMT)
