import QtQuick

Item {



    //  FPS 刷新计时器
    Timer{
        id: to_auto_timer
        interval: 1000
        onTriggered: {
            to_auto_true_count -= 1
        }
    }
    function start_to_auto_timer(){
        to_auto_timer.start()
    }


    Timer{
        interval: 150
        repeat: true

        onTriggered: {
            app_api.get_data(cool_bed_model_type.cool_bed_key,
                             (text)=>{
                                coolBedDataType.set_data_str(text)
                             },
                             (err)=>{
                                console.log("get_data error")
                             }

                             )



        }
    }
}
