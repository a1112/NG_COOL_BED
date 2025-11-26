import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core

ColumnLayout {
    id: root
    spacing: 6
    property var directionOptions: ["默认", "上", "下", "左", "右", "前", "后"]

    Label {
        text: qsTr("对象管理（Area）")
        font.bold: true
        color: "#ffffff"
    }

    ScrollView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        ColumnLayout {
            width: parent.width
            spacing: 8
            Repeater {
                model: Core.CalibrationViewCore.objectSettings
                delegate: Frame {
                    required property var modelData
                    property int itemIndex: index
                    Layout.fillWidth: true
                    background: Rectangle { color: "#191919"; radius: 4 }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4
                        Label {
                            text: modelData.camera
                            color: "#80cbc4"
                            font.bold: true
                        }
                        RowLayout {
                            spacing: 6
                            Label { text: qsTr("方向"); color: "#b0bec5" }
                            ComboBox {
                                Layout.fillWidth: true
                                model: root.directionOptions
                                currentIndex: {
                                    const options = root.directionOptions
                                    if (!options.indexOf) return -1
                                    const idx = options.indexOf(modelData.direction)
                                    return idx >= 0 ? idx : 0
                                }
                                onActivated: function(idx) {
                                    Core.CalibrationViewCore.updateObjectSetting(itemIndex, "direction", root.directionOptions[idx])
                                }
                            }
                        }
                        RowLayout {
                            spacing: 6
                            Label { text: "W"; color: "#b0bec5" }
                            SpinBox {
                                from: 0
                                to: 10000
                                value: modelData.width
                                onValueModified: Core.CalibrationViewCore.updateObjectSetting(itemIndex, "width", value)
                            }
                            Label { text: "H"; color: "#b0bec5" }
                            SpinBox {
                                from: 0
                                to: 10000
                                value: modelData.height
                                onValueModified: Core.CalibrationViewCore.updateObjectSetting(itemIndex, "height", value)
                            }
                        }
                    }
                }
            }
        }
    }

    Button {
        Layout.fillWidth: true
        text: qsTr("保存对象配置")
        enabled: Core.CalibrationViewCore.objectSettings.length > 0
        onClicked: Core.CalibrationViewCore.saveObjectSettings()
    }
}
