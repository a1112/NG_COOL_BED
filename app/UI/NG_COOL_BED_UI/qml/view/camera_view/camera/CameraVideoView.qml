import QtQuick
import QtMultimedia

Item {
    id: root
    property string rtspUrl: ""
    property bool offline: false
    property alias error: player.error
    property alias errorString: player.errorString
    property alias playbackState: player.playbackState
    property alias audioOutput: audio

    MediaPlayer {
        id: player
        autoPlay: !root.offline
        source: root.offline ? "" : root.rtspUrl
        audioOutput: audio
        videoOutput: video
    }

    AudioOutput {
        id: audio
        muted: true
        volume: 0.0
    }

    VideoOutput {
        id:video
        anchors.fill: parent
        visible: !root.offline && root.rtspUrl !== "" && player.error === MediaPlayer.NoError
        fillMode: VideoOutput.PreserveAspectFit
    }
}
