import QtQuick

Item {


    property var data: {return {}}

    property bool left_cool_bed_has_steel: data["left_cool_bed_has_steel"]
    property bool right_cool_bed_has_steel: data["left_cool_bed_has_steel"]

    property bool left_roll_bed_has_steel: data["left_roll_bed_has_steel"]
    property bool right_roll_bed_has_steel: data["right_roll_bed_has_steel"]

    function set_data_str(text){
        data = JSON.parse(text)

    }

}
