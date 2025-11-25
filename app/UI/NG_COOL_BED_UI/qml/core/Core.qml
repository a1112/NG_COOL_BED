import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../api" as ApiMod

pragma Singleton
Item {
    property string title_text: qsTr("冷床下料定位系统")
    property int  app_index: 0
    property var global_info: ({})
    property bool debug: !!(global_info && global_info["debug"])
    property var app_dict: ({})
    property var global_map_info: ({})

    // 工具/接口实例
    property ApiMod.Tool tool: ApiMod.Tool {}
    property ApiMod.Api api: ApiMod.Api

    property ListModel coolBedListModel: ListModel { }

    onGlobal_infoChanged: {
        console.log("global_info ", global_info)
        coolBedListModel.clear()
        const allList = global_info && global_info["all"] ? global_info["all"] : []
        tool.for_list(allList,(key,index)=>{
            const runList = global_info && global_info["run"] ? global_info["run"] : []
            const dataMap = global_info && global_info["data"] ? global_info["data"] : {}
            coolBedListModel.append({
                cool_bed_key_: key,
                run_: tool.in_list(key, runList),
                data_: JSON.stringify(dataMap[key] || {})
            })
        })
        app_dict = global_info && global_info["app"] ? global_info["app"] : {}
    }

    function flush(){
        api.get_info((text)=>{
            try { global_info = JSON.parse(text) } catch(e) { console.log("global_info parse error", e) }
        },(err)=>{
            console.log("global_info get error  ",err)
        })

        api.get_map(
                    (text)=>{
                        try { global_map_info = JSON.parse(text) } catch(e) { console.log("get_map parse error", e) }
                    },(err)=>{
                        console.log("get_map error  ",err)
                    }
                    )

    }

    Component.onCompleted: {
        flush()
    }
}
