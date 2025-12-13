import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia
import "."

Rectangle {
    id: root
    property var camera
    property int slotNumber: -1
    property bool selected: false
    property bool offlineMode: false
    property string imageSourceKey: "camera_stream"
    property bool showOverlay: true
    property var visibilityMap: ({})
    property var shapesProvider: null    // function(cameraId) -> shapes
    readonly property bool showLiveStream: imageSourceKey === "camera_stream"
    readonly property string _snapshotPath: camera ? (camera.snapshot || "") : ""
    readonly property string _sdkCapturePath: camera ? (camera.sdk_capture || "") : ""
    readonly property string offlineImageSource: (imageSourceKey === "sdk_capture" && _sdkCapturePath.length)
                                                 ? _sdkCapturePath
                                                 : _snapshotPath

    color: "#0f0f0f"
    radius: 4
    border.color: selected ? "#4fc3f7" :
                 ((videoView.error !== MediaPlayer.NoError || (!root.offlineMode && (!camera || !camera.rtsp_url))) ? "#d32f2f" : "#303030")
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 6
        spacing: 6

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: camera ? (camera.label || camera.id || camera.camera || "未命名相机") : "空槽"
                color: "#fff"
                font.bold: true
            }
            Label {
                text: camera && camera.position ? camera.position : ""
                color: "#9e9e9e"
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            Label {
                text: camera && camera.ip ? camera.ip : ""
                color: "#8bc34a"
                font.pixelSize: 12
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            CameraVideoView {
                id: videoView
                anchors.fill: parent
                rtspUrl: camera ? camera.rtsp_url : ""
                offline: root.offlineMode || !root.showLiveStream || !camera || !camera.rtsp_url
            }

            CameraImageView {
                id: offlineImage
                anchors.fill: parent
                visible: videoView.offline
                sourcePath: root.offlineImageSource
            }

            PerspectiveOverlay {
                id: overlayCanvas
                anchors.fill: parent
                showOverlay: root.showOverlay
                shapes: root.shapesProvider ? root.shapesProvider(camera ? camera.id : "") : []
                visibilityMap: root.visibilityMap
                visible: showOverlay && !!camera
            }

            Rectangle {
                anchors.fill: parent
                color: "#66000000"
                visible: (!root.offlineMode && (!camera || !camera.rtsp_url)) ||
                         (!videoView.offline && videoView.error !== MediaPlayer.NoError)
                Label {
                    anchors.centerIn: parent
                    text: (!root.offlineMode && (!camera || !camera.rtsp_url)) ? "无视频 / 未配置" :
                          (videoView.errorString || "连接失败")
                    color: "#ff5252"
                    font.bold: true
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: camera ? ("#" + camera.seq) : ""
                color: "#9e9e9e"
                font.pixelSize: 12
            }
            Label {
                text: root.footerText()
                color: "#9e9e9e"
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
        }
    }

    function footerText() {
        if (!camera) return ""
        if (imageSourceKey === "camera_stream")
            return camera.rtsp_url || camera.snapshot || ""
        if (imageSourceKey === "sdk_capture")
            return camera.sdk_capture || camera.snapshot || ""
        return camera.snapshot || ""
    }
}
