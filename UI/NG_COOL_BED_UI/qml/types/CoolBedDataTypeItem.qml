import QtQuick

Item {


    property var data


    property bool left_cool_bed_has_steel: data["left_cool_bed_has_steel"]
    property bool right_cool_bed_has_steel: data["right_cool_bed_has_steel"]

    property bool left_roll_bed_has_steel: data["left_roll_bed_has_steel"]
    property bool right_roll_bed_has_steel: data["right_roll_bed_has_steel"]



    property string use_group_key : data["group_key"]
    property bool has_error : data["has_error"]

    property var left_under_steel_to_center: data["left_under_steel_to_center"]
    property var right_under_steel_to_center: data["left_under_steel_to_center"]

    property var left_cool_bed_steel_to_up: data["left_cool_bed_steel_to_up"]
    property var right_cool_bed_steel_to_up: data["right_cool_bed_steel_to_up"]


    property var objcet_list: data["objects"]
    onObjcet_listChanged: {
        objcetList.clear()
        app_tool.for_list(data["objects"], (item) =>{
                            objcetList.append(item)
                          })
    }


    property ListModel objcetList: ListModel{

    }

}
