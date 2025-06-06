import QtQuick
import QtQuick.Controls


Menu {

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
        }
        MenuItem{
                    text: qsTr("labelimg")
        }
    }
}
