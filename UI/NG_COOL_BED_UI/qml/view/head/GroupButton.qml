import QtQuick
import QtQuick.Controls.Material

TabButton {
    text: "组："+ index
    ToolTip.visible: hovered
    ToolTip.text: "key " + group_key_
    onClicked: {
        cool_bed_core.flush_auto(false)

    }

    Rectangle{
        anchors.fill: parent
        color: "#00000000"
        border.color: "blue"
        border.width: 1
        visible: group_key_ ===  cool_bed_core.coolBedDataType.use_item.use_group_key

    }
}
