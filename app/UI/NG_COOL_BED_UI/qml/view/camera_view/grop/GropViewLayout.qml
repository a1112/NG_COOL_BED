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

    ColumnLayout {
        anchors.fill: parent
        spacing: 6

        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Label {
                text: (layoutConfig && layoutConfig.name) ? layoutConfig.name : "组合视图"
                color: "#fff"
                font.bold: true
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
