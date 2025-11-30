import QtQuick

Item {

    property var all_data:{return {}}

    property CoolBedDataTypeItem current_item: CoolBedDataTypeItem{
        data: all_data[cool_bed_core.current_key]

    }
    property CoolBedDataTypeItem use_item: CoolBedDataTypeItem{
        data: all_data["current"]
    }

    function set_data_str(text){
        // console.log(text)
        all_data = JSON.parse(text)
    }

}
