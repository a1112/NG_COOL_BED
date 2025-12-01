import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../core" as Core
import "../../../../base"


ColumnLayout {
    id: root
    spacing: 6
    property var directionOptions: ["默认", "左上", "右上", "右下", "左下"]

    Label {
        text: qsTr("对象管理（Area）")
        font.bold: true
        color: "#ffffff"
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: 12
        Label {
            text: qsTr("透视方向: %1").arg(Core.CalibrationViewCore.cameraOrderForCurrent().join(" -> "))
            color: "#bbbbbb"
        }
        Label {
            property var size: Core.CalibrationViewCore.cameraSizeForCurrent()
            text: qsTr("透视像素: %1 x %2").arg(size.width).arg(size.height)
            color: "#bbbbbb"
        }
    }

    ScrollView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        ColumnLayout {
            width: parent.width
            spacing: 8
            Repeater {
                model: Core.CalibrationViewCore.labelShapes
                delegate: ItemDelegate {
                    required property var modelData
                    required property int index
                    width: parent.width
                    text: (modelData.label || qsTr("形状%1").arg(index + 1)) +
                          qsTr("  点数: %1").arg((modelData.points || []).length)
                    contentItem: ColumnLayout {
                        spacing: 4
                        Label {
                            text: parent.text
                            color: "#e0e0e0"
                        }
                        Repeater {
                            model: modelData.points || []
                            delegate: Label {
                                required property var modelData
                                text: qsTr("点%1: (%2, %3)").arg(index + 1)
                                                           .arg(modelData[0].toFixed(1))
                                                           .arg(modelData[1].toFixed(1))
                                color: "#b0bec5"
                            }
                        }
                    }
                }
            }
        }
    }

    ActionButton {
        Layout.fillWidth: true
        text: qsTr("保存标注")
        enabled: (Core.CalibrationViewCore.labelShapes || []).length > 0
        onClicked: Core.CalibrationViewCore.saveLabelForCamera()
    }
}
