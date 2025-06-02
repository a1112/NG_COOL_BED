import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls.Material

import "../base"

HeadBase {
    id:root
    Layout.fillWidth: true
    height: 35
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
            text: "(1.0.0)"
        }


        Item{
            Layout.fillWidth: true
        }
        ItemDelegate{
            height: root.height
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
            width: 20
            height: 1
        }

    }
}
