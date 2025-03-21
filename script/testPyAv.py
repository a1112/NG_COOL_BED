import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
import av

def cap():
    container = av.open('rtsp://admin:ng123456@192.168.1.101/stream',options={
        '-c:v': 'libx264',
        '-preset': 'slow',  # 编码速度（slow=质量优先）
        '-crf': '23',  # 恒定质量模式（0-51，值越小质量越高）
        '-s': '1280x720',  # 输出分辨率
        'filter_complex': 'fps = 5'  # 设置帧率为30fps
                })# 1440, 2560
    #path_to_video是你视频的路径
    container_cap = container.decode(video=0)
    t = tqdm()
    while True:
        frame=next(container_cap)
        image=frame.to_image()
        t.update(1)
        cv_image = np.array(image)
        cv2.imshow('frame', cv_image)
        print(cv_image.shape)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap()