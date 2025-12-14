import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts


Item {
    id: root
    width: Layout.preferredWidth > 0 ? Layout.preferredWidth : 500
    implicitHeight: contentRow.implicitHeight
    property string key: ""
    property string value: ""
    property string msg: ""
    property alias hovered: idet.hovered

    property alias key_color: key_id.color
    property alias value_color: value_id.color

    ItemDelegate{
        id:idet
        anchors.fill: parent
        ToolTip.visible: hovered && msg
        ToolTip.text: msg
    }

    RowLayout{
        id: contentRow
        anchors.fill: parent
        Label{
            font.bold: true
            id : key_id
            text:  key+" : "
        }

        Label{
            id:value_id
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            font.bold: true
            text:  value
            background: Rectangle{color: "#000" }
        }
    }
}
