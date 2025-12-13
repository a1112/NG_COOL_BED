import QtQuick
import QtQuick.Layouts
import QtMultimedia
import "../view_core"
Item {
    Layout.fillWidth: true
    Layout.fillHeight: true

    property MapConfigItem map_config_item: MapConfigItem{
        draw_width:map_view.width
        draw_height: map_view.height

    }

    property real displayWidth: videoOutput.contentRect.width > 0 ? videoOutput.contentRect.width : videoOutput.width
    property real displayHeight: videoOutput.contentRect.height > 0 ? videoOutput.contentRect.height : videoOutput.height

    MediaPlayer {
        id: videoPlayer
        videoOutput: videoOutput
        autoPlay: true
        loops: MediaPlayer.Infinite

        source: cool_bed_core.video_url
        onErrorOccurred: {
            console.warn("video error:", errorString)
            streamReconnectTimer.restart()
        }
        onPlaybackStateChanged: {
            if (playbackState === MediaPlayer.StoppedState && source) {
                streamReconnectTimer.restart()
            }
        }
    }

    Connections {
        target: cool_bed_core
        function onVideo_urlChanged() {
            restartStream()
        }
    }

    function restartStream() {
        streamReconnectTimer.stop()
        if (!cool_bed_core.video_url || cool_bed_core.video_url.length === 0) {
            videoPlayer.stop()
            return
        }
        videoPlayer.stop()
        videoPlayer.source = ""
        videoPlayer.source = cool_bed_core.video_url
        videoPlayer.play()
    }

    Timer {
        id: streamReconnectTimer
        interval: 2000
        repeat: false
        onTriggered: restartStream()
    }

    VideoOutput {
        id: videoOutput
        anchors.fill: parent
        fillMode: VideoOutput.PreserveAspectFit

    }

    MapView{
        id:map_view
        anchors.centerIn: parent
        width: displayWidth
        height: displayHeight
    }

    ObjView{
        visible: cool_bed_core.show_det_view
        anchors.centerIn: parent
        width: displayWidth
        height: displayHeight
    }
    MoveView{
        id:move_view
        anchors.centerIn: parent
        width: displayWidth
        height: displayHeight

    }

    Rectangle {
        id: autoModeBadge
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 12
        color: "#66000000"
        radius: 4
        border.color: "#ffffff"
        border.width: 1
        visible: cool_bed_core.coolBedDataType.current_item.auto_mode.length > 0
        Text {
            color: "#ffffff"
            font.bold: true
            anchors.centerIn: parent
            padding: 8
            text: qsTr("模式: %1").arg(cool_bed_core.coolBedDataType.current_item.auto_mode)
        }
    }
}
