# CameraViw.qml 设计
    api 返回 相机信息表：
        拍摄的冷床，相机ip,rtsp_url,相机序号，相机位置。
    数据来源1： IpList.json 
    界面功能：
        界面分为左右区域，左侧区域显示分组以及IP，右侧区域显示视图
    左侧，左侧为 1 个 ListView + 1个 TreeView(文档 https://doc.qt.io/qt-6/qml-qtquick-treeview.html)
    ListView 主要为分组视图，目前固定为3个分组
        1，全部相机 （4*4布局）布局为 [[1，n/a,n/a,6],[2,3,4,5],[7，13,n/a,12],[8,9,10,11]]
        2,一号冷床（2*4） [[1，n/a,n/a,6],[2,3,4,5]]
        3,二号冷床（2*4） [[7，13,n/a,12],[8,9,10,11]]
    TreeView 根据 IpList.json 的形式排序Tree 

    右侧视图则是 使用     MediaPlayer，VideoOutput
    相机视图的 透视变化标注绘制：
        通过 当前使用的 CameraManage.json  找到 使用到相机的 group 组合，
            CameraManage.json 调整：
                camera_list：["L2_7"] 这种直接指定相机的，更改为
                camera_list：[{
                            "camera":"L2_7",
                            "shape":"Area"
                        }]
                camera_list 在 labelme 标注的json 中匹配（不区分大小写）到对呀的透视区域，增加了相机复用的功能
        视图增加页眉（组合显示的不需要），页眉中用多选来显示隐藏 画框视图（注意缩放）

    注意连接失败的红色显示，
    
    在离线模式下，依旧保留视图的显示，但是从rtsp_url 图像流更改为 只显示 当前标定组 中的 图像