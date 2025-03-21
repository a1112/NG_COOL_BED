"""
入口

"""
from multiprocessing import freeze_support
from ProjectManagement import Main
from Server import ApiServer


if __name__=="__main__":
    freeze_support()
    # 启动 HTTP 服务
    ApiServer.start()
    # 启动运行线程
    Main.main()