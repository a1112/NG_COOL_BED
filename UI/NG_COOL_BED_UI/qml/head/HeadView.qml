import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls.Material

import "../base"

HeadBase {
    Layout.fillWidth: true
    height: 35
    RowLayout{
        anchors.fill: parent
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
