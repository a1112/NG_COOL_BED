import QtQuick

Item {

    readonly property string cool_bed_key: cool_bed_model_type.cool_bed_key
    onCool_bed_keyChanged: {
        app_api.get_map(cool_bed_key, (text)=>{
                            map_data = JSON.parse(text)
                        }, (err)=>{
                        })
    }


    property var map_data: {return {}}


}
