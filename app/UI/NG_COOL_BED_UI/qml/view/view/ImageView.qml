import QtQuick
import QtQuick.Layouts
import QtMultimedia
import "../view_core"
Item {
    Layout.fillWidth: true
    Layout.fillHeight: true

    property bool tsFallbackUsedA: false
    property bool jpgFallbackUsedA: false
    property bool tsFallbackUsedB: false
    property bool jpgFallbackUsedB: false

    property bool frameReadyA: false
    property bool frameReadyB: false

    property int imageRefreshIndex: 0

    property int activeSlot: 0
    property int pendingSlot: -1
    property bool switching: pendingSlot !== -1

    readonly property VideoOutput activeVideoOutput: activeSlot === 0 ? videoOutputA : videoOutputB

    property MapConfigItem map_config_item: MapConfigItem{
        draw_width:map_view.width
        draw_height: map_view.height

    }

    property real displayWidth: activeVideoOutput.contentRect.width > 0 ? activeVideoOutput.contentRect.width : activeVideoOutput.width
    property real displayHeight: activeVideoOutput.contentRect.height > 0 ? activeVideoOutput.contentRect.height : activeVideoOutput.height

    Connections {
        target: cool_bed_core
        function onVideo_urlChanged() {
            startSwitch(cool_bed_core.video_url)
        }
    }

    function playerFor(slot) {
        return slot === 0 ? playerA : playerB
    }

    function frameReady(slot) {
        return slot === 0 ? frameReadyA : frameReadyB
    }

    function setFrameReady(slot, ready) {
        if (slot === 0) frameReadyA = ready
        else frameReadyB = ready
    }

    function resetFallback(slot) {
        if (slot === 0) {
            tsFallbackUsedA = false
            jpgFallbackUsedA = false
            frameReadyA = false
        } else {
            tsFallbackUsedB = false
            jpgFallbackUsedB = false
            frameReadyB = false
        }
    }

    function markTsFallbackUsed(slot) {
        if (slot === 0) tsFallbackUsedA = true
        else tsFallbackUsedB = true
    }

    function markJpgFallbackUsed(slot) {
        if (slot === 0) jpgFallbackUsedA = true
        else jpgFallbackUsedB = true
    }

    function tsFallbackUsed(slot) {
        return slot === 0 ? tsFallbackUsedA : tsFallbackUsedB
    }

    function jpgFallbackUsed(slot) {
        return slot === 0 ? jpgFallbackUsedA : jpgFallbackUsedB
    }

    function maybeCommitSwitch(slot) {
        if (slot !== pendingSlot) return
        var player = playerFor(slot)
        if (player.error !== MediaPlayer.NoError) return
        if (player.playbackState !== MediaPlayer.PlayingState)
            return
        if (!frameReady(slot))
            return
        commitSwitch()
    }

    function commitSwitch() {
        if (pendingSlot === -1) return
        var oldSlot = activeSlot
        activeSlot = pendingSlot
        pendingSlot = -1

        var oldPlayer = playerFor(oldSlot)
        oldPlayer.stop()
        oldPlayer.source = ""
        resetFallback(oldSlot)
    }

    function refreshOverlayImage() {
        if (!cool_bed_core || !cool_bed_core.current_key || cool_bed_core.current_key.length === 0)
            return
        imageRefreshIndex += 1
        overlayImage.source = app_api.get_image_url(
                    cool_bed_core.cool_bed_key,
                    cool_bed_core.current_key,
                    imageRefreshIndex,
                    cool_bed_core.show_mask)
    }

    function onPlayerError(slot, errorString) {
        var player = playerFor(slot)
        console.warn("video error:", errorString)
        if (player.source) {
            var src = player.source.toString()
            if (!tsFallbackUsed(slot) && src.indexOf("fmt=png") !== -1) {
                markTsFallbackUsed(slot)
                var fallbackTs = src.replace("fmt=png", "fmt=ts")
                console.warn("fallback to ts:", fallbackTs)
                player.stop()
                player.source = fallbackTs
                setFrameReady(slot, false)
                player.play()
                return
            }
            if (!jpgFallbackUsed(slot) && src.indexOf("fmt=ts") !== -1) {
                markJpgFallbackUsed(slot)
                var fallbackJpg = src.replace("fmt=ts", "fmt=jpg")
                console.warn("fallback to mjpeg:", fallbackJpg)
                player.stop()
                player.source = fallbackJpg
                setFrameReady(slot, false)
                player.play()
                return
            }
        }
        streamReconnectTimer.restart()
    }

    function startSwitch(url) {
        streamReconnectTimer.stop()
        if (!url || url.length === 0) {
            playerA.stop()
            playerA.source = ""
            playerB.stop()
            playerB.source = ""
            pendingSlot = -1
            overlayRefreshTimer.stop()
            overlayImage.source = ""
            return
        }

        // Immediately show /image as a placeholder before video has the first frame.
        refreshOverlayImage()
        overlayRefreshTimer.restart()

        var activePlayer = playerFor(activeSlot)
        if (!activePlayer.source || activePlayer.source.toString().length === 0) {
            resetFallback(activeSlot)
            pendingSlot = -1
            activePlayer.stop()
            activePlayer.source = url
            setFrameReady(activeSlot, false)
            activePlayer.play()
            return
        }
        var nextSlot = 1 - activeSlot
        pendingSlot = nextSlot
        resetFallback(nextSlot)

        var nextPlayer = playerFor(nextSlot)
        nextPlayer.stop()
        nextPlayer.source = url
        setFrameReady(nextSlot, false)
        nextPlayer.play()

        // Instant switch: swap immediately, keep overlay until first video frame arrives.
        commitSwitch()
    }

    Timer {
        id: streamReconnectTimer
        interval: 2000
        repeat: false
        onTriggered: startSwitch(cool_bed_core.video_url)
    }

    VideoOutput {
        id: videoOutputA
        anchors.fill: parent
        fillMode: VideoOutput.PreserveAspectFit
        visible: activeSlot === 0
    }

    VideoOutput {
        id: videoOutputB
        anchors.fill: parent
        fillMode: VideoOutput.PreserveAspectFit
        visible: activeSlot === 1
    }

    readonly property bool overlayVisible: {
        if (!cool_bed_core || !cool_bed_core.video_url || cool_bed_core.video_url.length === 0)
            return false
        var player = playerFor(activeSlot)
        if (player.error !== MediaPlayer.NoError) return true
        return !frameReady(activeSlot)
    }

    onOverlayVisibleChanged: {
        if (overlayVisible) {
            refreshOverlayImage()
            overlayRefreshTimer.restart()
        } else {
            overlayRefreshTimer.stop()
        }
    }

    Timer {
        id: overlayRefreshTimer
        interval: 200
        repeat: true
        running: false
        onTriggered: refreshOverlayImage()
    }

    Image {
        id: overlayImage
        anchors.fill: parent
        visible: overlayVisible
        fillMode: Image.PreserveAspectFit
        asynchronous: true
        cache: false
    }

    MediaPlayer {
        id: playerA
        videoOutput: videoOutputA
        autoPlay: true
        loops: MediaPlayer.Infinite
        onErrorOccurred: onPlayerError(0, errorString)
        onPlaybackStateChanged: {
            if (playbackState === MediaPlayer.StoppedState && source && activeSlot === 0) {
                streamReconnectTimer.restart()
            } else {
                maybeCommitSwitch(0)
            }
        }
    }

    MediaPlayer {
        id: playerB
        videoOutput: videoOutputB
        autoPlay: true
        loops: MediaPlayer.Infinite
        onErrorOccurred: onPlayerError(1, errorString)
        onPlaybackStateChanged: {
            if (playbackState === MediaPlayer.StoppedState && source && activeSlot === 1) {
                streamReconnectTimer.restart()
            } else {
                maybeCommitSwitch(1)
            }
        }
    }

    Connections {
        target: videoOutputA.videoSink
        function onVideoFrameChanged(frame) {
            if (!frameReadyA) frameReadyA = true
        }
    }

    Connections {
        target: videoOutputB.videoSink
        function onVideoFrameChanged(frame) {
            if (!frameReadyB) frameReadyB = true
        }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 10
        color: "#66000000"
        radius: 4
        border.color: "#ffffff"
        border.width: 1
        visible: switching
        Text {
            anchors.centerIn: parent
            color: "#ffffff"
            font.bold: true
            padding: 8
            text: qsTr("视频切换中...")
        }
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
        anchors.centerIn: parent
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

    Component.onCompleted: startSwitch(cool_bed_core.video_url)
}
