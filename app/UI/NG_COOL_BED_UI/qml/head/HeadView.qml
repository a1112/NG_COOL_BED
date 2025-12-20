import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls.Material

import "../base"
import "../menus" as Menus

HeadBase {
    id:root
    property var windowItem: null
    property var settingView: null
    property var sendDialog: null
    property var db6Dialog: null
    property var mapDialog: null
    property var algTestDialog: null
    property var ipSettingDialog: null
    Layout.fillWidth: true
    height: 45
    RowLayout{
        anchors.fill: parent
        spacing: 10
        Item{
            width: 20
            height: 1
        }
        ItemDelegate{
            id: mainMenuButton
            width: 32
            height: root.height - 10
            font.bold: true
            icon.source: Qt.resolvedUrl("../../icons/menu.png")
            Material.foreground: Material.BlueGrey
            onClicked: {
                mainMenu.popup(mainMenuButton, 0, mainMenuButton.height)
            }
        }
        Label {
                Material.foreground: Material.BlueGrey
                font.pointSize: 20
                font.bold: true
                text: app_core.title_text
        }
        Label {
            Material.foreground: Material.Pink
            font.pointSize: 13
            font.bold: true
            text: "(1.0.2)"
        }
        Label{
            text:app_core.debug ? "   测试模式" : "   在线模式"
            font.pointSize: 15
            font.bold: true
            Material.foreground: app_core.debug ? Material.Yellow : Material.Green
        }

        MainTabView{
        }
        Item{
            Layout.fillWidth: true
        }

        TestBtns{
            visible: app_core.debug
        }

        ActionButton{
            text: qsTr("算法测试")
            implicitHeight: root.height - 10
            onClicked: {
                if (algTestDialog && algTestDialog.openDialog) {
                    algTestDialog.openDialog()
                }
            }
        }

        ItemDelegate{
            height: root.height-5
            implicitHeight: height
            text: "SEND  - " + (
                    sendDialog && sendDialog.send_data
                    && sendDialog.send_data["I_NAI_W0_ALV_CNT"] !== undefined
                    ? sendDialog.send_data["I_NAI_W0_ALV_CNT"]
                    : "--")
            background: Rectangle{
                border.color: "blue"
                border.width: 1
                color: "#00000000"
            }
            onClicked: {
                if (sendDialog) {
                    sendDialog.open_()
                }
            }
        }

        Label {
            textFormat: Text.RichText

            font.pointSize: 10

            text: "  API: <a href=\""+app_api.server_url.serverUrl+"\">"+app_api.server_url.serverUrl+"</a>"
            onLinkActivated: (link)=>{
                             Qt.openUrlExternally(link)
                             }
        }
        Item{
            width: 10
            height: 1
        }
        SettingButton{
            height: root.height
            width: height
            iconSource: Qt.resolvedUrl("../../icons/setting.png")
            onClicked: {
                if (root.settingView) {
                    root.settingView.open()
                }
            }
        }

        Item{
            width: 5
            height: 1
        }
    }

    Menus.MainMenu{
        id: mainMenu
        windowItem: root.windowItem
        sendDialog: root.sendDialog
        db6Dialog: root.db6Dialog
        mapDialog: root.mapDialog
        algTestDialog: root.algTestDialog
        ipSettingDialog: root.ipSettingDialog
    }
}
