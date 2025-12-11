import QtQuick
import QtQuick.Controls.Material

TabButton {
    readonly property var priorityData: (cool_bed_core.coolBedDataType && cool_bed_core.coolBedDataType.all_data) ? cool_bed_core.coolBedDataType.all_data[group_key_] : null
    readonly property int priorityLevel: priorityData && priorityData["priority_level"] ? priorityData["priority_level"] : 3
    readonly property string priorityReason: priorityData && priorityData["priority_reason"] ? priorityData["priority_reason"] : ""
    readonly property bool shielded: priorityData && priorityData["shielded"]

    text: "组：" + index + " (P" + priorityLevel + (shielded ? "·屏蔽" : "") + ")"
    ToolTip.visible: hovered
    ToolTip.text: "key " + group_key_ + "\n优先级：" + priorityLevel + (priorityReason ? ("\n" + priorityReason) : "")
    Material.foreground: shielded ? Material.Grey : (priorityLevel <= 1 ? Material.Red : (priorityLevel === 2 ? Material.Orange : Material.BlueGrey))
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
