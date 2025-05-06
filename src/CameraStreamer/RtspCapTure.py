from tqdm import tqdm
import time
# from queue import Queue



from multiprocessing import  Queue
from CameraStreamer.ConversionImage import ConversionImage
from Configs.CameraConfig import CameraConfig
from Configs.GlobalConfig import GlobalConfig
from Loger import logger
from .ImageBuffer import ImageBuffer
from .CameraSdk import DebugCameraSdk, OpenCvCameraSdk, AvCameraSdk, HkCameraSdk
from CONFIG import DEBUG_MODEL, CapTureBaseClass, CAP_MODEL, CapModelEnum
from Save.ImageSave import CameraImageSave


class RtspCapTure(CapTureBaseClass): # Process, Thread
    def __init__(self, camera_config:CameraConfig, global_config:GlobalConfig):
        super().__init__()
        self.conversion = None
        self.camera_config = camera_config
        self.cool_bed_key = camera_config.cool_bed_key
        self.camera_key = camera_config.camera_key
        print(camera_config.camera_key)
        self.config = camera_config.config
        self.global_config = global_config

        self.ip = camera_config.ip
        self.rtsp_url = camera_config.rtsp_url
        self.cap = None
        self.camera_buffer = Queue()

        self.camera_image_save = None
        self.start()


    def get_video_capture(self):
        if CAP_MODEL == CapModelEnum.DEBUG:
            return DebugCameraSdk(self.camera_key)
        if CAP_MODEL == CapModelEnum.OPENCV:
            return OpenCvCameraSdk(self.camera_key, self.rtsp_url)
        if CAP_MODEL == CapModelEnum.AV:
            return AvCameraSdk(self.camera_key, self.rtsp_url)
        if CAP_MODEL == CapModelEnum.SDK:
            return HkCameraSdk(self.camera_key, self.ip)


    def run(self):
        self.camera_config = CameraConfig(self.cool_bed_key, self.camera_key)
        # self.conversion = self.camera_config.conversion
        self.conversion: ConversionImage    # 图像转换
        logger.debug(f"start RtspCapTure {self.camera_key}")
        self.cap = self.get_video_capture()
        self.camera_image_save = CameraImageSave(self.camera_config)
        # ret, frame = cap.read()
        index = 0
        num = 0
        while self.camera_config.enable:
            buffer = ImageBuffer(self.camera_config)
            ret, frame = self.cap.read()
            buffer.ret = ret
            buffer.frame = frame
            index += 1
            if frame is None:
                print("相机为空")
                self.cap.release()
                time.sleep(2)
                self.cap = self.get_video_capture()
                continue
            self.camera_image_save.save_first_buffer(buffer)    # 保存第一帧图像

            self.camera_buffer.put(buffer)
            # self.camera_
            buffer.show_frame()
            # buffer.show()
            self.camera_buffer.get() if self.camera_buffer.qsize() > 1 else time.sleep(0.01)
            num += 1

            if DEBUG_MODEL:  # 测试模式
                time.sleep(0.5)
            else:
                pass
                # if num % 500 == 1:
                #     self.camera_image_save.save_buffer(buffer)
            time.sleep(0.1)