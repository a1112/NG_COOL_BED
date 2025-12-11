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
}
