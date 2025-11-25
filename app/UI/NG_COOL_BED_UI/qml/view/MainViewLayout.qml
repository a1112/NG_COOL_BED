import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "camera_view"


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

            // 相机视图：占位，后续可按参考项目填充实际逻辑
            CameraViw{

            }
        }
    }
}

