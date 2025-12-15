import QtQuick
import QtWebSockets

Item {
    property var lastPayload: ({})

    property WebSocket db6Socket: WebSocket {
        id: db6Socket
        active: false
        url: ""
        onStatusChanged: {
            if (status === WebSocket.Error || status === WebSocket.Closed) {
                reconnectTimer.start()
            }
        }
        onTextMessageReceived: function(message) {
            try {
                lastPayload = JSON.parse(message)
            } catch(e) {
                console.warn("ws/db6_data parse error", e)
                db6Socket.active = false
                reconnectTimer.start()
            }
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
        return app_api.server_url.wsServerUrl + "/ws/db6_data"
    }

    function openSocket() {
        var url = socketUrl()
        if (!url) return
        db6Socket.active = false
        db6Socket.url = url
        db6Socket.active = true
    }

    Component.onCompleted: openSocket()
}
