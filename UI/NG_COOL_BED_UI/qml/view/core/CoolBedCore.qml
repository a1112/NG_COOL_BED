import QtQuick
import "../../types"
Item {

    property TimeCore timeCore: TimeCore{}

    property bool auto_check: true  // 自动设置

    property int current_index: 0


    readonly property string cool_bed_key: cool_bed_model_type.cool_bed_key

    readonly property string current_key: cool_bed_model_type.get_key(current_index)

    property int cap_index : 0

    property string source_url: app_api.get_image_url(cool_bed_model_type.cool_bed_key, current_key, cap_index,cool_bed_core.show_mask)

    property CoolBedDataType coolBedDataType: CoolBedDataType{}


    function flush_source(){
        cap_index += 1
    }



    function flush_auto(auto_){
        auto_check = auto_
        if (!auto_){
            to_auto_true_count = 100
        }
    }

    property int to_auto_true_count : 0
    onTo_auto_true_countChanged: {
        if (to_auto_true_count>0){
            timeCore.start_to_auto_timer()
        }
        else{
            flush_auto(true)
        }
    }


    property bool show_map_view: true
    property bool show_det_view: true

    property bool can_show_mask: true// This is available in all editors.
    property bool show_mask: false

}
