# coding=utf-8
import queue
import time
import logging

import cv2
import numpy as np

from Base import RollingQueue
from .HCNetSDK import *
from .PlayCtrl import *
from threading import Thread
from Loger import logger
import CONFIG
sdk_logger = logging.getLogger("hk_sdk")
sdk_logger.setLevel(logging.INFO)

class DevClass(Thread):
    def __init__(self):
        super().__init__()
        self.hikSDK, self.playM4SDK = self.LoadSDK()  # 加载sdk库
        self.iUserID = -1  # 登录句柄
        self.lRealPlayHandle = -1  # 预览句柄
        self.wincv = None  # windows环境下的参数
        self.win = None  # 预览窗口
        self.FuncDecCB = None  # 解码回调
        self.PlayCtrlPort = C_LONG(-1)  # 播放通道号
        self.basePath = ''  # 基础路径
        self.preview_file = ''  # linux预览取流保存路径
        self.funcRealDataCallBack_V30 = REALDATACALLBACK(self.RealDataCallBack_V30)  # 预览回调函数
        self.frame_queue = RollingQueue(maxsize=1)  # 限制队列大小防止内存溢出
        self.FPS = 10
        self.last_time = time.time()
        self._fps_last_ts = time.time()
        self._fps_count = 0

        # self.start()
        # self.msg_callback_func = MSGCallBack_V31(self.g_fMessageCallBack_Alarm)  # 注册回调函数实现

    def LoadSDK(self):
        hikSDK = None
        playM4SDK = None
        try:
            sdk_logger.debug("netsdkdllpath: %s", netsdkdllpath)
            hikSDK = load_library(netsdkdllpath)
            playM4SDK = load_library(playM4dllpath)
        except OSError as e:
            sdk_logger.error("动态库加载失败: %s", e)
        return hikSDK, playM4SDK

    # 设置SDK初始化依赖库路径
    def SetSDKInitCfg(self):
        # 设置HCNetSDKCom组件库和SSL库加载路径
        if sys_platform == 'windows':
            basePath = os.getcwd().encode('gbk')
            base_dir = b'\\lib'
            sdk_logger.debug("basePath %s", basePath + base_dir)
            strPath = basePath + base_dir
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath 
            sdk_logger.debug("strPath: %s", strPath)
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SDK_PATH.value,
                                                 byref(sdk_ComPath)):
                sdk_logger.debug("NET_DVR_SetSDKInitCfg: 2 Succ")
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_LIBEAY_PATH.value,
                                                 create_string_buffer(strPath + b'\\libcrypto-1_1-x64.dll')):
                sdk_logger.debug("NET_DVR_SetSDKInitCfg: 3 Succ")
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SSLEAY_PATH.value,
                                                 create_string_buffer(strPath + b'\\libssl-1_1-x64.dll')):
                sdk_logger.debug("NET_DVR_SetSDKInitCfg: 4 Succ")
        else:
            basePath = os.getcwd().encode('utf-8')
            sdk_logger.debug("%s", basePath)
            strPath = basePath + b'\\lib'
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SDK_PATH.value,
                                                 byref(sdk_ComPath)):
                sdk_logger.debug("NET_DVR_SetSDKInitCfg: 2 Succ")
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_LIBEAY_PATH.value,
                                                 create_string_buffer(strPath + b'/libcrypto.so.1.1')):
                sdk_logger.debug("NET_DVR_SetSDKInitCfg: 3 Succ")
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SSLEAY_PATH.value,
                                                 create_string_buffer(strPath + b'/libssl.so.1.1')):
                sdk_logger.debug("NET_DVR_SetSDKInitCfg: 4 Succ")
        self.basePath = basePath

        try:
            sdk_logger.debug("尝试加载SDK: %s", playM4dllpath)
            playM4SDK = CDLL(playM4dllpath)
            sdk_logger.debug("SDK加载成功，获取版本信息...")
            if hasattr(playM4SDK, 'PlayM4_GetSDKVersion'):
                version = playM4SDK.PlayM4_GetSDKVersion()
                sdk_logger.debug("PlayM4 SDK版本: %s", version)
            self.playM4SDK = playM4SDK
            return self.playM4SDK
        except Exception as e:
            sdk_logger.error("动态库加载失败: %s", e)
            return None


    # 通用设置，日志/回调事件类型等
    def GeneralSetting(self):

        # 日志的等级（默认为0）：0-表示关闭日志，1-表示只输出ERROR错误日志，2-输出ERROR错误信息和DEBUG调试信息，3-输出ERROR错误信息、DEBUG调试信息和INFO普通信息等所有信息
        # self.hikSDK.NET_DVR_SetLogToFile(3, b'./SdkLog_Python/', False)
        self.hikSDK.NET_DVR_SetLogToFile(3, bytes('./SdkLog_Python/', encoding="utf-8"), False)

    # 登录设备
    def LoginDev(self, ip, username, pwd):
        # 登录参数，包括设备地址、登录用户、密码等
        struLoginInfo = NET_DVR_USER_LOGIN_INFO()
        struLoginInfo.bUseAsynLogin = 0  # 同步登录方式
        struLoginInfo.sDeviceAddress = ip  # 设备IP地址
        struLoginInfo.wPort = 8000  # 设备服务端口
        struLoginInfo.sUserName = username  # 设备登录用户名
        struLoginInfo.sPassword = pwd  # 设备登录密码
        struLoginInfo.byLoginMode = 0

        # 设备信息, 输出参数
        struDeviceInfoV40 = NET_DVR_DEVICEINFO_V40()

        self.iUserID = self.hikSDK.NET_DVR_Login_V40(byref(struLoginInfo), byref(struDeviceInfoV40))
        if self.iUserID < 0:
            print("Login failed, error code: %d" % self.hikSDK.NET_DVR_GetLastError())
            self.hikSDK.NET_DVR_Cleanup()
        else:
            print('登录成功，设备序列号：%s' % str(struDeviceInfoV40.struDeviceV30.sSerialNumber, encoding="utf8").rstrip('\x00'))

    # 登出设备
    def LogoutDev(self):
        if self.iUserID > -1:
            # 撤销布防，退出程序时调用
            self.hikSDK.NET_DVR_Logout(self.iUserID)
    def DecCBFun(self, nPort, pBuf, nSize, pFrameInfo, nUser, nReserved2):
        try:
            if (time.time() - self.last_time) < (1 / self.FPS):
                return
            self.last_time = time.time()
            if not pFrameInfo:
                return
            if pFrameInfo.contents.nType != 3:
                return

            nWidth = int(pFrameInfo.contents.nWidth or 0)
            nHeight = int(pFrameInfo.contents.nHeight or 0)
            if nWidth <= 0 or nHeight <= 0 or nSize <= 0 or not pBuf:
                return

            buf_type = (c_ubyte * nSize).from_address(addressof(pBuf.contents))
            yuv_data = np.frombuffer(buf_type, dtype=np.uint8)

            expected_size = nWidth * nHeight * 3 // 2
            if yuv_data.size != expected_size:
                return

            yuv_frame = yuv_data.reshape((nHeight * 3 // 2, nWidth))
            rgb_frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2RGB_IYUV)

            now = time.time()
            self._fps_count += 1
            if now - self._fps_last_ts >= 2.0:
                fps = self._fps_count / (now - self._fps_last_ts)
                if CONFIG.camera_fps_show:
                    logger.info("DecCBFun fps=%.2f", fps)
                self._fps_count = 0
                self._fps_last_ts = now

            self.frame_queue.put(rgb_frame)
        except Exception:
            # ctypes 回调里抛异常会打印 "Exception ignored ..."；这里吞掉并记录 debug 以免刷屏
            logger.debug("DevClass.DecCBFun callback error", exc_info=True)
            return

    def DecCBFun_1(self, nPort, pBuf, nSize, pFrameInfo, nUser, nReserved2):
        # 解码回调函数
        from pathlib import Path
        import CONFIG
        if pFrameInfo.contents.nType == 3:
            # 解码返回视频YUV数据，将YUV数据转成jpg图片保存到本地
            # 如果有耗时处理，需要将解码数据拷贝到回调函数外面的其他线程里面处理，避免阻塞回调导致解码丢帧
            sFileName = (fr'./pic/{CONFIG.IP}/test_stamp[%d].jpg' % pFrameInfo.contents.nStamp)
            Path(sFileName).parent.mkdir(exist_ok=True)
            nWidth = pFrameInfo.contents.nWidth
            nHeight = pFrameInfo.contents.nHeight
            nType = pFrameInfo.contents.nType
            dwFrameNum = pFrameInfo.contents.dwFrameNum
            nStamp = pFrameInfo.contents.nStamp
            print(nWidth, nHeight, nType, dwFrameNum, nStamp, sFileName)

            lRet = self.playM4SDK.PlayM4_ConvertToJpegFile(pBuf, nSize, nWidth, nHeight, nType,
                                                           c_char_p(sFileName.encode()))
            if lRet == 0:
                print('PlayM4_ConvertToJpegFile fail, error code is:', self.playM4SDK.PlayM4_GetLastError(nPort))
            else:
                print('PlayM4_ConvertToJpegFile success')

    # 将视频流保存到本地
    def writeFile(self, filePath, pBuffer, dwBufSize):
        # 使用memmove函数将指针数据读到数组中
        data_array = (c_byte * dwBufSize)()
        memmove(data_array, pBuffer, dwBufSize)

        # 判断文件路径是否存在
        if not os.path.exists(filePath):
            # 如果不存在，使用 open() 函数创建一个空文件
            open(filePath, "w").close()

        preview_file_output = open(filePath, 'ab')
        preview_file_output.write(data_array)
        preview_file_output.close()

    def RealDataCallBack_V30(self, lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
        try:
            play_sdk = getattr(self, "playM4SDK", None)
            if not play_sdk:
                return
            if dwDataType == NET_DVR_SYSHEAD:
                play_sdk.PlayM4_SetStreamOpenMode(self.PlayCtrlPort, 0)
                if play_sdk.PlayM4_OpenStream(
                        self.PlayCtrlPort, pBuffer, dwBufSize, 1024 * 1024
                ):
                    self.FuncDecCB = DECCBFUNWIN(self.DecCBFun)
                    play_sdk.PlayM4_SetDecCallBackExMend(
                        self.PlayCtrlPort, self.FuncDecCB, None, 0, None
                    )
                    play_sdk.PlayM4_Play(self.PlayCtrlPort, 0)
            elif dwDataType == NET_DVR_STREAMDATA:
                play_sdk.PlayM4_InputData(self.PlayCtrlPort, pBuffer, dwBufSize)
        except Exception:
            logger.debug("DevClass.RealDataCallBack_V30 callback error", exc_info=True)
            return

    def startPlay(self):
        # 获取一个播放句柄
        if not self.playM4SDK.PlayM4_GetPort(byref(self.PlayCtrlPort)):
            print(f'获取播放库句柄失败, 错误码：{self.playM4SDK.PlayM4_GetLastError(self.PlayCtrlPort)}')
            # 开始预览
        preview_info = NET_DVR_PREVIEWINFO()
        preview_info.hPlayWnd = 0
        preview_info.lChannel = 1  # 通道号
        preview_info.dwStreamType = 0  # 主码流
        preview_info.dwLinkMode = 0  # TCP
        preview_info.bBlocked = 1  # 阻塞取流

        # 开始预览并且设置回调函数回调获取实时流数据
        self.lRealPlayHandle = self.hikSDK.NET_DVR_RealPlay_V40(self.iUserID, byref(preview_info),
                                                                self.funcRealDataCallBack_V30,
                                                                None)
        if self.lRealPlayHandle < 0:
            print('Open preview fail, error code is: %d' % self.hikSDK.NET_DVR_GetLastError())
            # 登出设备
            self.hikSDK.NET_DVR_Logout(self.iUserID)
            # 释放资源
            self.hikSDK.NET_DVR_Cleanup()
            exit()
        import tkinter
        self.win = tkinter.Tk()
        if sys_platform == 'windows1':
            import tkinter
            from tkinter import Button

            # 创建窗口
            self.win = tkinter.Tk()
            # 固定窗口大小
            self.win.resizable(0, 0)
            self.win.overrideredirect(True)

            sw = self.win.winfo_screenwidth()
            # 得到屏幕宽度
            sh = self.win.winfo_screenheight()
            # 得到屏幕高度

            # 窗口宽高
            ww = 512
            wh = 384
            x = (sw - ww) / 2
            y = (sh - wh) / 2
            self.win.geometry("%dx%d+%d+%d" % (ww, wh, x, y))

            # 创建退出按键
            b = Button(self.win, text='退出', command=self.win.quit)
            b.pack()
            # 创建一个Canvas，设置其背景色为白色
            self.wincv = tkinter.Canvas(self.win, bg='white', width=ww, height=wh)
            self.wincv.pack()

            # 开始预览
            preview_info = NET_DVR_PREVIEWINFO()
            preview_info.hPlayWnd = 0
            preview_info.lChannel = 1  # 通道号
            preview_info.dwStreamType = 0  # 主码流
            preview_info.dwLinkMode = 0  # TCP
            preview_info.bBlocked = 1  # 阻塞取流

            # 开始预览并且设置回调函数回调获取实时流数据
            self.lRealPlayHandle = self.hikSDK.NET_DVR_RealPlay_V40(self.iUserID, byref(preview_info),
                                                                    self.funcRealDataCallBack_V30,
                                                                    None)
            if self.lRealPlayHandle < 0:
                print('Open preview fail, error code is: %d' % self.hikSDK.NET_DVR_GetLastError())
                # 登出设备
                self.hikSDK.NET_DVR_Logout(self.iUserID)
                # 释放资源
                self.hikSDK.NET_DVR_Cleanup()
                exit()

            # show Windows
            self.win.mainloop()

    def stopPlay(self):
        # 关闭预览
        self.hikSDK.NET_DVR_StopRealPlay(self.lRealPlayHandle)

        # 停止解码，释放播放库资源
        if self.PlayCtrlPort.value > -1:
            self.playM4SDK.PlayM4_Stop(self.PlayCtrlPort)
            self.playM4SDK.PlayM4_CloseStream(self.PlayCtrlPort)
            self.playM4SDK.PlayM4_FreePort(self.PlayCtrlPort)
            self.PlayCtrlPort = C_LONG(-1)

    def run(self):
        while True:
            print("run")
            frame = self.frame_queue.get()
            # 示例：显示帧
            cv2.imshow('Frame', frame)
            cv2.waitKey(1)


def cap_one(ip_):

    import CONFIG

    CONFIG.IP = ip_
    dev = DevClass()
    dev.SetSDKInitCfg()  # 设置SDK初始化依赖库路径
    dev.hikSDK.NET_DVR_Init()  # 初始化sdk
    dev.GeneralSetting()  # 通用设置，日志，回调函数等
    dev.LoginDev(ip=ip_, username=b"admin", pwd=b"ng123456")  # 登录设备

    dev.startPlay()  # playTime用于linux环境控制预览时长，windows环境无效
    print(dev)
    while True:
        time.sleep(1)
        print(dev.frame_queue.get())
    dev.stopPlay()
    dev.LogoutDev()
    # 释放资源
    dev.hikSDK.NET_DVR_Cleanup()

if __name__ == '__main__':
    from multiprocessing import Process, freeze_support
    freeze_support()
    Process(target=cap_one,args=(b'60.60.60.13',)).start()
    # Process(target=cap_one,args=(b'192.168.1.102',)).start()
    # Process(target=cap_one,args=(b'192.168.1.103',)).start()
    # Process(target=cap_one,args=(b'192.168.2.104',)).start()
    # Process(target=cap_one,args=(b'192.168.2.105',)).start()
    # Process(target=cap_one,args=(b'192.168.2.106',)).start()
    # Process(target=cap_one,args=(b'192.168.3.107',)).start()
    # Process(target=cap_one,args=(b'192.168.3.108',)).start()
    # Process(target=cap_one,args=(b'192.168.3.109',)).start()
    # Process(target=cap_one,args=(b'192.168.4.110',)).start()
    # Process(target=cap_one,args=(b'192.168.4.111',)).start()
    # Process(target=cap_one,args=(b'192.168.4.112',)).start()
