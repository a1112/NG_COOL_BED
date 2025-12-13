import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "."
import "../../../core" as Core

Item {
    id: root
    anchors.fill: parent

    property var layoutConfig: Core.CameraViewCore.currentLayoutConfig()
    property bool offlineMode: Core.CameraViewCore.offlineMode
    property bool showOverlay: Core.CameraViewCore.showOverlay
    property int selectedSlot: Core.CameraViewCore.selectedSlotNumber
    property var visibilityMap: Core.CameraViewCore.overlayVisibility
    property var shapesProvider: function(camId){ return Core.CameraViewCore.shapesForCamera(camId) }
    property var selectedCamera: (Core.CameraViewCore && Core.CameraViewCore.cameraForSlot)
                                 ? Core.CameraViewCore.cameraForSlot(selectedSlot)
                                 : null
    property string selectedImageSourceKey: Core.CameraViewCore.selectedImageSourceKey
    readonly property string selectedImageUrl: {
        if (!selectedCamera)
            return ""
        if (selectedImageSourceKey === "sdk_capture" && selectedCamera.sdk_capture)
            return selectedCamera.sdk_capture
        return selectedCamera.snapshot || ""
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 6

        Label {
            Layout.fillWidth: true
            text: Core.CameraViewCore.calibrateKey && Core.CameraViewCore.calibrateKey.length
                  ? qsTr("标定分组：%1").arg(Core.CameraViewCore.calibrateKey)
                  : qsTr("标定分组：未加载")
            color: "#81c784"
            font.pixelSize: 16
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Label {
                text: (layoutConfig && layoutConfig.name) ? layoutConfig.name : "组合视图"
                color: "#fff"
                font.bold: true
            }
            Text {
                visible: root.offlineMode && selectedImageUrl !== ""
                textFormat: Text.RichText
                wrapMode: Text.NoWrap
                clip: true
                color: "#64b5f6"
                Layout.preferredWidth: 360
                Layout.maximumWidth: 480
                text: visible ? ("<a href=\"" + selectedImageUrl + "\">" + selectedImageUrl + "</a>") : ""
                onLinkActivated: function(link) { Qt.openUrlExternally(link) }
            }
            Label {
                text: offlineMode ? "调试/离线模式" : ""
                color: "#9e9e9e"
            }
            Item { Layout.fillWidth: true }
        }

        ScrollView {
            id: videoScroll
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            GropView {
                width: videoScroll.width
                layoutConfig: root.layoutConfig
                cameraForSlot: Core.CameraViewCore.cameraForSlot
                selectedSlot: root.selectedSlot
                offlineMode: root.offlineMode
                showOverlay: root.showOverlay
                visibilityMap: root.visibilityMap
                shapesProvider: root.shapesProvider
            }
        }
    }
}
