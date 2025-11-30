import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."
import "grop"
import "camera"
import "left"
import "../../core" as Core

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    SplitView {
        anchors.fill: parent
        spacing: 10

        Frame {
            SplitView.preferredWidth: 320
            SplitView.fillHeight: true
            padding: 8
            background: Rectangle { color: "#1a1a1a"; radius: 4 }

            LeftManageView {
                anchors.fill: parent
            }
        }

        Frame {
            SplitView.fillWidth: true
            SplitView.fillHeight: true
            padding: 8
            background: Rectangle { color: "#121212"; radius: 4 }

            ColumnLayout {
                anchors.fill: parent
                spacing: 8

                ScrollView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Core.CameraViewCore.overlayLabels.length ? 36 : 0
                    visible: Core.CameraViewCore.overlayLabels.length > 0 && Core.CameraViewCore.showOverlay
                    clip: true
                    contentItem: Flickable {
                        contentWidth: flow.implicitWidth
                        contentHeight: flow.implicitHeight
                        interactive: false
                        Flow {
                            id: flow
                            spacing: 8
                            Repeater {
                                model: Core.CameraViewCore.overlayLabels
                                delegate: CheckBox {
                                    required property string modelData
                                    text: modelData
                                    checked: Core.CameraViewCore.overlayVisibility[modelData.toLowerCase()] !== false
                                    onToggled: Core.CameraViewCore.setOverlayVisibility(modelData, checked)
                                }
                            }
                        }
                    }
                }

                Loader {
                    id: bodyLoader
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    sourceComponent: Core.CameraViewCore.selectedLayoutType === 0 ? gropBody : cameraBody
                }
            }

            Component {
                id: gropBody
                GropViewLayout {
                    // layoutConfig: Core.CameraViewCore.currentLayoutConfig()
                    // selectedSlot: Core.CameraViewCore.selectedSlotNumber
                    // offlineMode: Core.CameraViewCore.offlineMode
                    // showOverlay: Core.CameraViewCore.showOverlay
                    // visibilityMap: Core.CameraViewCore.overlayVisibility
                    // shapesProvider: function(camId){ return Core.CameraViewCore.shapesForCamera(camId) }
                }
            }

            Component {
                id: cameraBody
                CameraViewLayout {
                    selectedSlot: Core.CameraViewCore.selectedSlotNumber
                    offlineMode: Core.CameraViewCore.offlineMode
                    showOverlay: Core.CameraViewCore.showOverlay
                    visibilityMap: Core.CameraViewCore.overlayVisibility
                    shapesProvider: function(camId){ return Core.CameraViewCore.shapesForCamera(camId) }
                }
            }
        }
    }
}
