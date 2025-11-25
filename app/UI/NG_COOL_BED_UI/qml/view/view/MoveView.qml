import QtQuick

Item {


    CoolBedMoveItem{
        value:cool_bed_core.coolBedDataType.current_item.left_cool_bed_steel_to_up
        x:map_config_item.cool_bed.x+map_config_item.cool_bed.width*(1/4)
        height:map_config_item.y_mm_asp * parseInt( cool_bed_core.coolBedDataType.current_item.left_cool_bed_steel_to_up)
    }
    CoolBedMoveItem{
        value:cool_bed_core.coolBedDataType.current_item.right_cool_bed_steel_to_up
        x:map_config_item.cool_bed.x+map_config_item.cool_bed.width*(3/4)
        height: map_config_item.y_mm_asp * parseInt( cool_bed_core.coolBedDataType.current_item.right_cool_bed_steel_to_up)
    }


}
