import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core

ScrollView {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true
    clip: true

    Column {
        id: container
        width: root.width
        spacing: 8

        Repeater {
            model: Core.CalibrationViewCore.lineGroupList
            delegate: Column {
                required property var modelData
                width: root.width
                spacing: 4

                Label {
                    text: qsTr("组别 %1").arg(modelData.lineKey)
                    font.bold: true
                    color: "#9bd8ff"
                }

                Repeater {
                    model: modelData.groupList
                    delegate: Frame {
                        required property var modelData
                        width: root.width
                        background: Rectangle { color: "#202020"; radius: 4 }
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 4
                            RowLayout {
                                spacing: 6
                                ToolButton {
                                    text: modelData.key
                                    checkable: true
                                    checked: Core.CalibrationViewCore.selectedGroupKey === modelData.key
                                    onClicked: Core.CalibrationViewCore.selectedGroupKey = modelData.key
                                }
                                Label {
                                    text: qsTr("优先级 %1").arg(modelData.priority)
                                    color: "#bbbbbb"
                                    font.pixelSize: 12
                                }
                                Label {
                                    text: qsTr("相机 %1").arg(modelData.cameraList.length)
                                    color: "#bbbbbb"
                                    font.pixelSize: 12
                                }
                            }
                            Text {
                                text: modelData.msg
                                color: "#d0d0d0"
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                            Flow {
                                Layout.fillWidth: true
                                spacing: 4
                                Repeater {
                                    model: modelData.cameraList
                                    delegate: Rectangle {
                                        id: chip
                                        implicitWidth: chipText.implicitWidth + 16
                                        implicitHeight: 22
                                        radius: 11
                                        color: "#333"
                                        Text {
                                            id: chipText
                                            anchors.centerIn: parent
                                            text: modelData.camera
                                            color: "#fafafa"
                                            font.pixelSize: 11
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
