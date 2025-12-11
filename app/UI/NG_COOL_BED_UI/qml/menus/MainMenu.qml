import QtQuick
import QtQuick.Controls
import QtQuick.Window

Menu {
    id: mainMenu

    property var windowItem: null
    property var sendDialog: null
    property var mapDialog: null
    property var algTestDialog: null
    property bool opencvDisplayEnabled: true
    property bool opencvDisplayBusy: false

    readonly property string _docsUrl: app_api && app_api.server_url
                                      ? (app_api.server_url.serverUrl + "/docs")
                                      : ""

    function openApp(name) {
        const dict = app_core && app_core.app_dict ? app_core.app_dict : null
        if (!dict || !dict[name]) {
            console.warn("[MainMenu] app not registered:", name)
            return
        }
        const normalized = dict[name].replace(/\\/g, "/")
        Qt.openUrlExternally("file:///" + normalized)
    }

    function toggleFullScreen() {
        if (!windowItem)
            return
        if (windowItem.visibility === Window.FullScreen)
            windowItem.showMaximized()
        else
            windowItem.showFullScreen()
    }

    function refreshOpenCvDisplay() {
        if (!app_api || !app_api.get_opencv_display)
            return
        opencvDisplayBusy = true
        app_api.get_opencv_display(
                    function(resp) {
                        opencvDisplayEnabled = !!(resp && resp.enable)
                        opencvDisplayBusy = false
                    },
                    function(err, status) {
                        console.warn("get_opencv_display failed", status, err)
                        opencvDisplayBusy = false
                    })
    }

    function setOpenCvDisplay(enable) {
        if (!app_api || !app_api.set_opencv_display)
            return
        opencvDisplayBusy = true
        app_api.set_opencv_display(
                    enable,
                    function(resp) {
                        opencvDisplayEnabled = !!(resp && resp.enable)
                        opencvDisplayBusy = false
                    },
                    function(err, status) {
                        console.warn("set_opencv_display failed", status, err)
                        opencvDisplayBusy = false
                    })
    }

    function toggleOpenCvDisplay() {
        if (opencvDisplayBusy)
            return
        setOpenCvDisplay(!opencvDisplayEnabled)
    }

    Menu {
        title: qsTr("系统")
        MenuItem {
            text: qsTr("刷新数据")
            onTriggered: {
                if (app_core && app_core.flush)
                    app_core.flush()
            }
        }
        MenuItem {
            text: qsTr("接口文档")
            enabled: _docsUrl.length > 0
            onTriggered: Qt.openUrlExternally(_docsUrl)
        }
    }

    Menu {
        title: qsTr("工具")
        MenuItem {
            text: qsTr("发送数据...")
            onTriggered: {
                if (sendDialog && sendDialog.open_)
                    sendDialog.open_()
            }
        }
        MenuItem {
            text: qsTr("映射数据...")
            onTriggered: {
                if (mapDialog && mapDialog.open_)
                    mapDialog.open_()
            }
        }
        MenuItem {
            text: qsTr("算法测试...")
            onTriggered: {
                if (algTestDialog && algTestDialog.openDialog)
                    algTestDialog.openDialog()
            }
        }
        MenuItem {
            text: qsTr("一键保存相机图像")
            onTriggered: {
                if (!app_api || !app_api.save_one_cap)
                    return
                app_api.save_one_cap(
                            function(text) {
                                var result = {}
                                try {
                                    result = JSON.parse(text)
                                } catch (e) {
                                    console.log("save_one_cap parse error", e)
                                }
                                var folder = result.folder || ""
                                if (folder.length > 0 && (result.count || 0) > 0) {
                                    var normalized = folder.replace(/\\/g, "/")
                                    Qt.openUrlExternally("file:///" + normalized)
                                }
                                console.log("save_one_cap success", JSON.stringify(result))
                            },
                            function(err, status) {
                                console.log("save_one_cap error", status, err)
                            })
            }
        }
        MenuItem {
            text: opencvDisplayEnabled
                  ? qsTr("关闭后端 OpenCV 显示")
                  : qsTr("开启后端 OpenCV 显示")
            enabled: !opencvDisplayBusy && app_api && app_api.set_opencv_display
            onTriggered: toggleOpenCvDisplay()
        }
        Menu {
            title: qsTr("打开应用")
            MenuItem {
                text: qsTr("LabelMe")
                enabled: app_core && app_core.app_dict && app_core.app_dict["labelme"]
                onTriggered: openApp("labelme")
            }
            MenuItem {
                text: qsTr("LabelImg")
                enabled: app_core && app_core.app_dict && app_core.app_dict["labelimg"]
                onTriggered: openApp("labelimg")
            }
        }
    }

    Menu {
        title: qsTr("视图")
        MenuItem {
            text: windowItem && windowItem.visibility === Window.FullScreen
                  ? qsTr("退出全屏")
                  : qsTr("进入全屏")
            onTriggered: toggleFullScreen()
        }
    }

    MenuSeparator { }

    MenuItem {
        text: qsTr("退出")
        onTriggered: Qt.quit()
    }

    Component.onCompleted: refreshOpenCvDisplay()
}
