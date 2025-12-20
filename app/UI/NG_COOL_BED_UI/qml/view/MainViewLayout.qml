import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "camera_view"
import "calibration_view"
import "../core" as Core


Item {
    id: root
    property var coolBedListModel: null

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        Component {
            id: mainViewComponent
            ColumnLayout {
                spacing: 0
                Layout.fillWidth: true
                Layout.fillHeight: true

                property var viewModel: root.coolBedListModel

                Repeater {
                    model: parent.viewModel
                    delegate: CoolBedView { }
                }
            }
        }

        Component {
            id: cameraViewComponent
            CameraViw { }
        }

        Component {
            id: calibrationViewComponent
            CalibrationView { }
        }

        Loader {
            id: viewLoader
            Layout.fillWidth: true
            Layout.fillHeight: true
            sourceComponent: {
                switch (app_core.app_index) {
                case 1:
                    return cameraViewComponent
                case 2:
                    return calibrationViewComponent
                default:
                    return mainViewComponent
                }
            }
        }
    }

    Connections {
        target: app_core
        function onApp_indexChanged() {
            if (app_core.app_index === 1) {
                Core.CameraViewCore.reloadFromServer()
                Core.CameraViewCore.refreshFromApi()
            }
        }
    }
}
