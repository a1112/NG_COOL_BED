import QtQuick

Item {
    property string title_text: qsTr("冷床下料定位系统")

    property var global_info: {return {}}
    property var app_dict: {return {}}
    property var global_map_info: {return {}}

    property ListModel coolBedListModel: ListModel{

    }

    onGlobal_infoChanged: {
        console.log("global_info ", global_info)
        coolBedListModel.clear()
        app_tool.for_list(global_info["all"],(key,index)=>{
                              coolBedListModel.append({
                                                          cool_bed_key_: key,
                                                          run_: app_tool.in_list(key,global_info["run"]),
                                                          data_: JSON.stringify(global_info["data"][key])
                                                      })
                          })
        app_dict = global_info["app"]
    }


    function flush(){
        app_api.get_info((text)=>{
                             // console.log("global_info ", text)
                             global_info = JSON.parse(text)
                         },(err)=>{
                             console.log("global_info get error  ",err)
                         })

        app_api.get_map(
                    (text)=>{
                        // console.log("global_info ", text)
                        global_map_info = JSON.parse(text)
                    },(err)=>{
                        console.log("get_map error  ",err)
                    }
                    )

    }



    Component.onCompleted: {
        flush()
    }

    property var test_value: {"all":["L1","L2"],
        "run":["L1","L2"],
        "data":{
            "L1":{
                "all":["L1_g0_2345","L1_g1_6","L1_g2_1"],
                "run":["L1_g0_2345","L1_g1_6","L1_g2_1"],
                "data":
                {"L1_g0_2345":
                    {"camera_list":["L1_2","L1_3","L1_4","L1_5"],
                        "calibrate":"calibrate","key":"L1_g0_2345","msg":" group L1  2,3,4,5 camera","priority":0,
                        "size_list":[[1024,1024],[1117,1024],[1117,1024],[1024,1024]]},
                    "L1_g1_6":
                    {"camera_list":["L1_6"],
                        "calibrate":"calibrate",
                        "key":"L1_g1_6",
                        "msg":" group right camera only",
                        "priority":3,
                        "size_list":[[3072,768]]
                    },
                    "L1_g2_1":{"camera_list":["L1_1"],
                        "calibrate":"calibrate",
                        "key":"L1_g2_1",
                        "msg":" group left camera only",
                        "priority":1,
                        "size_list":[[3072,768]]
                    }
                }
            },
            "L2":{"all":["L2_g0_2345","L2_g1_6","L2_g2_1"],"run":["L2_g0_2345","L2_g1_6","L2_g2_1"],"data":{"L2_g0_2345":{"camera_list":["L2_2","L2_3","L2_4","L2_5"],"calibrate":"calibrate","key":"L2_g0_2345","msg":" group L2  2,3,4,5 camera","priority":0,"size_list":[[1303,1024],[1117,1024],[1210,1024],[1117,1024]]},"L2_g1_6":{"camera_list":["L2_6"],"calibrate":"calibrate","key":"L2_g1_6","msg":" L2 right camera only","priority":1,"size_list":[[2048,768]]},"L2_g2_1":{"camera_list":["L2_1"],"calibrate":"calibrate","key":"L2_g2_1","msg":" L2 left camera only","priority":1,"size_list":[[2048,768]]}}}}}


}
