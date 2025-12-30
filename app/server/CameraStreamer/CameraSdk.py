#  回去圖像的 SDK
from abc import ABC, abstractmethod

from PIL import Image
import cv2
import numpy as np

import tool

from Configs.CameraManageConfig import camera_manage_config
from SDK.HkSdkCap import HkSdkCap

class CameraSdkBase(ABC):
    """
    基础类别
    """
    def __init__(self):
        pass

    @abstractmethod
    def read(self):
        ...

    @abstractmethod
    def release(self):
        ...


class AvCameraSdk(CameraSdkBase):

    def __init__(self, key, rtsp_url):
        super().__init__()
        self.key = key
        self.rtsp_url = rtsp_url
        self.det = 1
        # options = {
        #     "analyzeduration": "10000000",  # 设置analyzeduration选项为10秒
        #     "probesize": "5000000",  # 设置probesize选项为5000000字节
        #     'rtsp_transport': 'tcp',  # 设置RTSP传输协议，可以是"tcp"或"udp"
        #     'max_delay': '50000',  # 设置最大延迟
        #     'stimeout': '10000000',  # 设置超时时间，单位是微秒
        #     'allowed_media_types': '设置允许的媒体类型，例如["audio", "video"]",  # 未验证！！！
        #     'muxdelay': "设置最大复用延迟。",  # 未验证！！！
        #     'probesize2': "设置探测大小。"  # 未验证！！！
        # }

        container = av.open(self.rtsp_url, options = {
            '-c:v': 'libx264',
            '-preset': 'slow',  # 编码速度（slow=质量优先）
            '-crf': '23',  # 恒定质量模式（0-51，值越小质量越高）
            # 's': '1280x720',  # 输出分辨率
            '-vf': 'scale=1280:-2',  # 宽度x，高度自动保持比例（偶数调整）
            '-r': '10',  # 强制输出x fps（可能重复或丢弃帧）
            # '-vsync': 'vfr'  # 保持原始可变帧率（不推荐直播）
        })
        self.container = container
        self.container_cap = container.decode(video=0)



    def release(self):
        self.container.close()

    def read(self):
        self.det +=1
        cap_image = next(self.container_cap)

        try:
            # Convert with limited (TV) range metadata to avoid swscale warnings.
            cap_image = cap_image.reformat(format="rgb24", color_range="mpeg")
            image = cap_image.to_ndarray()
        except Exception:
            image = cap_image.to_image()
            image = np.array(image)

        return self.det, image



class OpenCvCameraSdk(CameraSdkBase):

    def __init__(self, key, rtsp_url):
        super().__init__()
        self.key = key
        self.rtsp_url = rtsp_url
        self.camera = cv2.VideoCapture(rtsp_url) # cv2.CAP_FFMPEG
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 100000)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)
        self.camera.set(cv2.CAP_PROP_FPS, 2)

    def read(self):
        det, img = self.camera.read()
        return det, img

    def release(self):
        return self.camera.release()



class DebugCameraSdk(CameraSdkBase):

    def __init__(self, key):
        super().__init__()
        self.key = key
        self.camera = None
        self.det = 0
        self.frame_url = camera_manage_config.get_debug_frame_url(self.key)
        print(f"debug model {self.frame_url}")
        self.frame = Image.open(str(self.frame_url))
        self.frame = np.array(self.frame)

    def read(self):
        self.det+=1
        return self.det, self.frame

    def release(self):
        pass

class HkCameraSdk(CameraSdkBase):

    def __init__(self, key, ip, username="admin", password="ng123456"):
        super().__init__()
        self.key = key
        self.ip = ip
        self.sdk = HkSdkCap(self.ip, username=username, password=password)

    def release(self):
        pass

    def read(self):
        return 0,self.sdk.get_last_frame()

