import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "."
import "../../../core" as Core

Item {
    id: root
    anchors.fill: parent
    property int selectedSlot: Core.CameraViewCore.selectedSlotNumber
    property bool offlineMode: Core.CameraViewCore.offlineMode
    property bool showOverlay: Core.CameraViewCore.showOverlay
    property var visibilityMap: Core.CameraViewCore.overlayVisibility
    property var shapesProvider: function(camId){ return Core.CameraViewCore.shapesForCamera(camId) }

    readonly property var currentCamera: (selectedSlot !== -1 && Core.CameraViewCore && Core.CameraViewCore.cameraForSlot)
        ? Core.CameraViewCore.cameraForSlot(selectedSlot) : null
    property string snapshotLink: (currentCamera && currentCamera.snapshot) ? currentCamera.snapshot : ""

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Label {
                text: currentCamera ? ("当前相机: #" + currentCamera.seq + " " + currentCamera.label) : "请选择左侧相机"
                color: "#fff"
                font.bold: true
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            Text {
                visible: root.offlineMode && snapshotLink !== ""
                textFormat: Text.RichText
                wrapMode: Text.NoWrap
                clip: true
                color: "#64b5f6"
                Layout.preferredWidth: 360
                Layout.maximumWidth: 480
                text: visible ? ("<a href=\"" + snapshotLink + "\">" + snapshotLink + "</a>") : ""
                onLinkActivated: function(link) { Qt.openUrlExternally(link) }
            }
            Label {
                text: offlineMode ? "调试/离线模式" : ""
                color: "#9e9e9e"
            }
        }

        CameraTile {
            Layout.fillWidth: true
            Layout.fillHeight: true
            camera: currentCamera
            slotNumber: currentCamera ? currentCamera.seq : -1
            selected: true
            offlineMode: root.offlineMode
            showOverlay: root.showOverlay
            visibilityMap: root.visibilityMap
            shapesProvider: root.shapesProvider
        }
    }
}
