import QtQuick
import "../view_core"
Item {
    id:root
    visible: cool_bed_core.show_map_view

    Rectangle{
        anchors.fill: parent
        color: "#00000000"
        border.color: "blue"
        border.width: 1
    }

    Rectangle{
        color: "#00000000"
        border.color: "green"
        border.width: 2
        x:map_config_item.cool_bed.x
        y:map_config_item.cool_bed.y
        width:map_config_item.cool_bed.width
        height:map_config_item.cool_bed.height
    }

    Rectangle{
        color: "#00000000"
        border.color: "yellow"
        border.width: 2
        x:map_config_item.up.x
        y:map_config_item.up.y
        width:map_config_item.up.width
        height:map_config_item.up.height
    }

    Rectangle{
        color: "#00000000"
        border.color: "pink"
        border.width: 2
        x:map_config_item.down.x
        y:map_config_item.down.y
        width:map_config_item.down.width
        height:map_config_item.down.height
    }

    Rectangle{
        // 中心
        color: "yellow"
        width: 2
        x:map_config_item.center_x-1
        y:0
        height:root.height
    }
}
