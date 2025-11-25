import QtQuick

Item {
    id: root

    function safeValue(v) { return (v === undefined || v === null) ? 0 : v }
    readonly property var currentItem: (cool_bed_core && cool_bed_core.coolBedDataType) ? cool_bed_core.coolBedDataType.current_item : null

    CoolBedMoveItem{
        value: root.safeValue(currentItem ? currentItem.left_cool_bed_steel_to_up : 0)
        x: (typeof map_config_item !== "undefined" && map_config_item && map_config_item.cool_bed) ? (map_config_item.cool_bed.x + map_config_item.cool_bed.width*(1/4)) : 0
        height: (typeof map_config_item !== "undefined" && map_config_item && map_config_item.y_mm_asp)
                ? (map_config_item.y_mm_asp * root.safeValue(currentItem ? currentItem.left_cool_bed_steel_to_up : 0)) : 0
    }
    CoolBedMoveItem{
        value: root.safeValue(currentItem ? currentItem.right_cool_bed_steel_to_up : 0)
        x: (typeof map_config_item !== "undefined" && map_config_item && map_config_item.cool_bed) ? (map_config_item.cool_bed.x + map_config_item.cool_bed.width*(3/4)) : 0
        height: (typeof map_config_item !== "undefined" && map_config_item && map_config_item.y_mm_asp)
                ? (map_config_item.y_mm_asp * root.safeValue(currentItem ? currentItem.right_cool_bed_steel_to_up : 0)) : 0
    }
}
