import QtQuick
import QtWebSockets

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


    property WebSocket dataSocket: WebSocket {
        id: dataSocket
        active: false
        url: ""
        onStatusChanged: {
            if (status === WebSocket.Error || status === WebSocket.Closed) {
                reconnectTimer.start()
            }
        }
        onTextMessageReceived: function(message) {
            coolBedDataType.set_data_str(message)
        }
    }

    Timer {
        id: reconnectTimer
        interval: 2000
        repeat: false
        onTriggered: openSocket()
    }

    function socketUrl() {
        if (!app_api || !app_api.server_url) return ""
        return app_api.server_url.wsServerUrl + "/ws/data/" + cool_bed_model_type.cool_bed_key
    }

    function openSocket() {
        const url = socketUrl()
        if (!url) return
        dataSocket.active = false
        dataSocket.url = url
        dataSocket.active = true
    }

    Component.onCompleted: openSocket()
}
