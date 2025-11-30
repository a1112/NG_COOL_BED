import QtQuick

Item {
    // 输入数据，默认空对象，避免未定义访问
    property var data: ({})

    property bool left_cool_bed_has_steel: false
    property bool right_cool_bed_has_steel: false

    property bool left_roll_bed_has_steel: false
    property bool right_roll_bed_has_steel: false

    property string use_group_key: ""
    property bool has_error: false

    property var left_under_steel_to_center: null
    property var right_under_steel_to_center: null

    property var left_cool_bed_steel_to_up: null
    property var right_cool_bed_steel_to_up: null

    property var left_rool_to_center: null
    property var right_rool_to_center: null

    property var objcet_list: []
    property ListModel objcetList: ListModel {}

    function updateFromData() {
        const d = data || {}
        left_cool_bed_has_steel = !!d["left_cool_bed_has_steel"]
        right_cool_bed_has_steel = !!d["right_cool_bed_has_steel"]

        left_roll_bed_has_steel = !!d["left_roll_bed_has_steel"]
        right_roll_bed_has_steel = !!d["right_roll_bed_has_steel"]

        use_group_key = d["group_key"] || ""
        has_error = !!d["has_error"]

        left_under_steel_to_center = d["left_under_steel_to_center"]
        right_under_steel_to_center = d["right_under_steel_to_center"]

        left_cool_bed_steel_to_up = d["left_cool_bed_steel_to_up"]
        right_cool_bed_steel_to_up = d["right_cool_bed_steel_to_up"]

        left_rool_to_center = d["left_rol_to_center"]
        right_rool_to_center = d["right_rol_to_center"]

        objcet_list = d["objects"] || []
        objcetList.clear()
        if (typeof app_tool !== "undefined" && app_tool && app_tool.for_list) {
            app_tool.for_list(objcet_list, function(item) { objcetList.append(item) })
        } else if (Array.isArray(objcet_list)) {
            objcet_list.forEach(function(item) { objcetList.append(item) })
        }
    }

    onDataChanged: updateFromData()
}
