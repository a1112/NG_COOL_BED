import CONFIG
import json

import cv2

def load_json(url):
    with open(url, "r", encoding = CONFIG.encoding ) as f:
        return json.load(f)

def show_cv2(img,title="image"):
    cv2.namedWindow(title, flags=cv2.WINDOW_NORMAL)
    cv2.imshow(title, img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return
