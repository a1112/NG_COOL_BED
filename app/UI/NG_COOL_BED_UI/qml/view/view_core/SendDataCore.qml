import QtQuick
import QtWebSockets

Item {
    property var lastPayload: ({})

    property WebSocket sendSocket: WebSocket {
        id: sendSocket
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
                console.warn("ws/send_data parse error", e)
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
        return app_api.server_url.wsServerUrl + "/ws/send_data"
    }

    function openSocket() {
        var url = socketUrl()
        if (!url) return
        sendSocket.active = false
        sendSocket.url = url
        sendSocket.active = true
    }

    Component.onCompleted: openSocket()
}
