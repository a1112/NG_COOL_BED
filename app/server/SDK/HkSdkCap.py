from threading import Thread

from .Devclass import DevClass

class HkSdkCap(Thread):
    def __init__(self, ip: str, username: str = "admin", password: str = "ng123456"):
        super().__init__()
        self.ip = ip.encode("gbk")
        print(fr"HkSdkCap {self.ip}")
        self.dev = DevClass()
        self.frame_queue =self.dev.frame_queue
        self.dev.SetSDKInitCfg()  # 设置SDK初始化依赖库路径
        self.dev.hikSDK.NET_DVR_Init()  # 初始化sdk
        self.dev.GeneralSetting()  # 通用设置，日志，回调函数等

        user_b = str(username or "admin").encode("gbk")
        pass_b = str(password or "").encode("gbk")
        if ip=="60.60.60.13":
            self.dev.LoginDev(ip=self.ip, username=b"admin", pwd=b"BKV_IESL")
        else:
            self.dev.LoginDev(ip=self.ip, username=user_b, pwd=pass_b)  # 登录设备

        self.dev.startPlay()  # playTime用于linux环境控制预览时长，windows环境无效

    def relace(self):
        self.dev.stopPlay()
        self.dev.LogoutDev()
        self.dev.hikSDK.NET_DVR_Cleanup()
    def get_last_frame(self):
        return self.frame_queue.get()
