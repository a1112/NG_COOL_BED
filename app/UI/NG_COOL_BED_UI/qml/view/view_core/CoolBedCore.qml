import QtQuick
import "../../types"
Item {

    property TimeCore timeCore: TimeCore{}

    property bool auto_check: true  // 自动设置

    property int current_index: 0


    readonly property string cool_bed_key: cool_bed_model_type.cool_bed_key

    readonly property string current_key: cool_bed_model_type.get_key(current_index)

    property int cap_index : 0
    property int video_reload_token: 0
    property string video_url: ""

    property ControlConfig controlConfig: ControlConfig{
    }

    property CoolBedDataType coolBedDataType: CoolBedDataType{}


    function flush_source(){
        refresh_video_source()
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

    function refresh_video_source(){
        cap_index += 1
        video_reload_token += 1
        video_url = app_api.get_video_url(
                    cool_bed_model_type.cool_bed_key,
                    current_key,
                    cool_bed_core.show_mask,
                    video_reload_token)
    }

    onShow_maskChanged: refresh_video_source()
    onCurrent_indexChanged: refresh_video_source()
    onCurrent_keyChanged: refresh_video_source()
    onCool_bed_keyChanged: refresh_video_source()
    onVideo_reload_tokenChanged: {}

    Component.onCompleted: refresh_video_source()
}
