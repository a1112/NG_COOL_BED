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
        StackLayout {
            id: stack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: app_core.app_index
            onCurrentIndexChanged: {
                if (currentIndex === 1) {
                    Core.CameraViewCore.reloadFromServer()
                    Core.CameraViewCore.refreshFromApi()
                }
            }

            // 主视图：沿用原有 CoolBedView 列表
            ColumnLayout {
                spacing: 0
                Layout.fillWidth: true
                Layout.fillHeight: true

                Repeater {
                    model: root.coolBedListModel
                    delegate: CoolBedView { }
                }
            }

            // 相机视图
            CameraViw {
            }

            // 标定视图
            CalibrationView {
            }
        }
    }
}
