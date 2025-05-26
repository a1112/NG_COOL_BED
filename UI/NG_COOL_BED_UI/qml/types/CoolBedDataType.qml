import QtQuick

Item {


    property var data: {return {}}

    property bool left_cool_bed_has_steel: data["left_cool_bed_has_steel"]
    property bool right_cool_bed_has_steel: data["left_cool_bed_has_steel"]

    property bool left_roll_bed_has_steel: data["left_roll_bed_has_steel"]
    property bool right_roll_bed_has_steel: data["right_roll_bed_has_steel"]



    property string use_group_key : data["group_key"]
    property bool has_error : data["has_error"]

    property var left_under_steel_to_center: data["left_under_steel_to_center"]
    property var right_under_steel_to_center: data["left_under_steel_to_center"]

    property var steel_list: []

    function set_data_str(text){
        console.log(text)
        data = JSON.parse(text)

    }

}
