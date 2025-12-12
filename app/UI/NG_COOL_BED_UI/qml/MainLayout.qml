import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls.Material
import "head"
import "core"
import "view"
import "view/view_core" as ViewCore
import "api"
import "dialogs"

ApplicationWindow {
    id: rootWindow

    width: Screen.width*0.7
    height: Screen.height*0.85
    visible: true
    background: Rectangle{color: "#000" }


    title: app_core.title_text
    ColumnLayout{
        anchors.fill: parent
        HeadView{   // 主菜单
            windowItem: rootWindow
            settingView: settingView
            sendDialog: send_dialog
            mapDialog: map_dialog
            algTestDialog: alg_test_dialog
        }
        MainViewLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            id:mainStackLayout
            coolBedListModel: app_core.coolBedListModel
        }
        // 设定弹窗
        SettingView {
            id: settingView
        }
        SendDialog {
            id: send_dialog
            send_data: sendDataCore && sendDataCore.lastPayload && sendDataCore.lastPayload.data
                        ? sendDataCore.lastPayload.data : ({})
            send_byte: sendDataCore && sendDataCore.lastPayload ? (sendDataCore.lastPayload.bytes || "") : ""
        }
        MapDialog {
            id: map_dialog
            send_data: sendDataCore && sendDataCore.lastPayload && sendDataCore.lastPayload.data
                        ? sendDataCore.lastPayload.data : ({})
            send_byte: sendDataCore && sendDataCore.lastPayload ? (sendDataCore.lastPayload.bytes || "") : ""
        }
        AlgTestDialog {
            id: alg_test_dialog
        }
        ViewCore.SendDataCore {
            id: sendDataCore
        }
    }
}
