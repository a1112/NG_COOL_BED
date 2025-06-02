import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Item {
    width: 300
    height: 30


    property alias key_color: key_id.color
    property alias value_color: value_id.color

    ItemDelegate{
        anchors.fill: parent
        ToolTip.visible: hovered
        ToolTip.text: app_config.key_to_msg(title)
    }

    RowLayout{
        anchors.fill: parent
    Label{
        font.bold: true
        id : key_id
        text:  title + " : "
    }

    Label{
        id:value_id
        Layout.fillWidth: true
        horizontalAlignment: Text.AlignHCenter
        font.bold: true
        text:  "" + value
        background: Rectangle{color: "#000" }
    }
    }
}
