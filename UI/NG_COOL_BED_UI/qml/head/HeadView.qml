import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls.Material

import "../base"

HeadBase {
    id:root
    Layout.fillWidth: true
    height: 45
    RowLayout{
        anchors.fill: parent
        spacing: 10
        Item{
            width: 20
            height: 1
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
            text: "(1.0.1)"
        }
        Label{
            text:""// app_core.debug ? "   测试" : "   在线"
            font.pointSize: 15
            font.bold: true
            Material.foreground:app_core.debug ? Material.Red : Material.Green
        }
        Item{
            Layout.fillWidth: true
        }

        TestBtns{
            visible: app_core.debug
        }

        ItemDelegate{
            height: root.height-5
            implicitHeight: height
            text: "SEND  - " + send_dialog.send_data["I_NAI_W0_ALV_CNT"]
            background: Rectangle{
                border.color: "blue"
                border.width: 1
                color: "#00000000"
            }
            onClicked: {
                send_dialog.open_()
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
            height: parent.height
            width: parent.width
            onClicked: {
                tool_menu.popup()
            }
        }


        Item{
            width: 5
            height: 1
        }
    }
}
