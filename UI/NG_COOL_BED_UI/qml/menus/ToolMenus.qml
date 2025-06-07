import QtQuick
import QtQuick.Controls


Menu {
    function has_app(name){
        let app_url =app_core.app_dict[name]
        if (app_url)
            return true
        return false
    }

    function open_app(name){
        let app_url =app_core.app_dict[name]
        Qt.openUrlExternally("file:///"+app_url)
    }

    MenuItem{
        text: qsTr("API DOC")
        onClicked: {
            Qt.openUrlExternally(app_api.server_url.serverUrl+"/docs")
        }

    }

    MenuItem{
        text: qsTr("发送数据")
        onClicked: send_dialog.open_()
    }

    MenuItem{
        text: qsTr("定位数据")
        onClicked: map_dialog.open_()
    }
    Menu{
        title: qsTr("打开")
        MenuItem{
                    text: qsTr("labelme")
                    onClicked: {
                        open_app("labelme")
                    }
        }
        MenuItem{
                    text: qsTr("labelimg")
                    onClicked: {
                        open_app("labelimg")
                    }
        }
    }
}
