import QtQuick

Item {
    property string cool_bed_key:cool_bed_key_



    property bool run:run_
    property string data_str:data_

    property var all_keys:[]

    property ListModel groupModel: ListModel{

    }

    function get_key(index){
        return all_keys[index]
    }

    property var data:JSON.parse(data_str)
    onDataChanged: {
        groupModel.clear()
        all_keys = data["all"]
        app_tool.for_list(data["all"], (key)=>{
                            groupModel.append({
                                        group_key_:key,
                                        run_:app_tool.in_list(key,data["run"]),
                                        data_:JSON.stringify(data["data"][key])
                                      })
                          })
    }





    property var tast_data:{
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
    }
}
