import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
import av
container = av.open('rtsp://admin:ng123456@192.168.1.101/stream')
#path_to_video是你视频的路径
container_cap = container.decode(video=0)
while True:
    frame=next(container_cap)
    image=frame.to_image()
    cv_image = np.array(image)
    cv2.imshow('frame', cv_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
