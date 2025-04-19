from threading import Thread

from Devclass import DevClass

class HkSdkCap(Thread):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self.dev=None
        self.frame_queue=None
        self.start()

    def run(self):
        self.dev = DevClass()
        self.frame_queue =self.dev.frame_queue
        self.dev.SetSDKInitCfg()  # 设置SDK初始化依赖库路径
        self.dev.hikSDK.NET_DVR_Init()  # 初始化sdk
        self.dev.GeneralSetting()  # 通用设置，日志，回调函数等
        self.dev.LoginDev(ip=self.ip, username=b"admin", pwd=b"ng123456")  # 登录设备

        self.dev.startPlay(playTime=10)  # playTime用于linux环境控制预览时长，windows环境无效
        self.dev.stopPlay()
        self.dev.LogoutDev()
        # 释放资源
        self.dev.hikSDK.NET_DVR_Cleanup()

    def get_last_frame(self):
        return self.frame_queue.get()