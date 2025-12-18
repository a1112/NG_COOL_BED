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

    property int retryIntervalMs: 2000
    property int retryCount: 0
    property bool _flushInFlight: false
    property bool _flushPending: false
    property real _activeFlushToken: 0

    Timer {
        id: retryTimer
        interval: retryIntervalMs
        repeat: false
        onTriggered: flush()
    }

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
        if (!api || !api.get_info || !api.get_map) return
        if (_flushInFlight) {
            _flushPending = true
            return
        }

        _flushInFlight = true
        _flushPending = false
        retryTimer.stop()

        const token = Date.now() + Math.random()
        _activeFlushToken = token

        let infoDone = false
        let mapDone = false
        let infoOk = false
        let mapOk = false

        function finish() {
            if (_activeFlushToken !== token) return
            if (!infoDone || !mapDone) return

            _flushInFlight = false

            if (_flushPending) {
                flush()
                return
            }

            if (infoOk && mapOk) {
                retryCount = 0
                retryTimer.stop()
                return
            }

            retryCount += 1
            if (!retryTimer.running) retryTimer.start()
        }

        api.get_info((text)=>{
            if (_activeFlushToken !== token) return
            try {
                global_info = JSON.parse(text)
                infoOk = true
            } catch(e) {
                console.log("global_info parse error", e)
            }
            infoDone = true
            finish()
        },(err, status)=>{
            if (_activeFlushToken !== token) return
            console.log("global_info get error", status, err)
            infoDone = true
            finish()
        })

        api.get_map(
                    (text)=>{
                        if (_activeFlushToken !== token) return
                        try {
                            global_map_info = JSON.parse(text)
                            mapOk = true
                        } catch(e) {
                            console.log("get_map parse error", e)
                        }
                        mapDone = true
                        finish()
                    },(err, status)=>{
                        if (_activeFlushToken !== token) return
                        console.log("get_map error", status, err)
                        mapDone = true
                        finish()
                    }
                    )
    }

    Component.onCompleted: {
        flush()
    }
}
