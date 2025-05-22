import QtQuick
import QtQuick.Controls.Material

TabButton {
    text: "组："+ index
    ToolTip.visible: hovered
    ToolTip.text: "key " + group_key_
    onClicked: {
        cool_bed_core.flush_auto(false)

    }
}
