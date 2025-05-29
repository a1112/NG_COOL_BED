import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Item {
    width: 300
    height: 30

    property string msg: ""

    property alias key_color: key_id.color
    property alias value_color: value_id.color

    ItemDelegate{
        anchors.fill: parent
        ToolTip.visible: hovered && msg
        ToolTip.text: msg
    }

    RowLayout{
        anchors.fill: parent
    Label{
        font.bold: true
        id : key_id
        text:  title+" : "
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
