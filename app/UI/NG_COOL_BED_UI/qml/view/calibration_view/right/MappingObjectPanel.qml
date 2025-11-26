import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core

ColumnLayout {
    id: root
    spacing: 6

    Label {
        text: qsTr("对象设置（XML）")
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
                model: Core.CalibrationViewCore.mappingObjects
                delegate: Frame {
                    required property var modelData
                    property int itemIndex: index
                    Layout.fillWidth: true
                    background: Rectangle { color: "#1f1f1f"; radius: 4 }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4
                        Label {
                            text: modelData.name
                            color: "#81d4fa"
                            font.bold: true
                        }
                        GridLayout {
                            rowSpacing: 6
                            columnSpacing: 8
                            columns: 2
                            Label { text: "xmin"; color: "#bdbdbd" }
                            SpinBox {
                                from: 0
                                to: Core.CalibrationViewCore.mappingImageWidth
                                value: modelData.xmin
                                onValueModified: Core.CalibrationViewCore.updateMappingObject(itemIndex, { xmin: value })
                            }
                            Label { text: "ymin"; color: "#bdbdbd" }
                            SpinBox {
                                from: 0
                                to: Core.CalibrationViewCore.mappingImageHeight
                                value: modelData.ymin
                                onValueModified: Core.CalibrationViewCore.updateMappingObject(itemIndex, { ymin: value })
                            }
                            Label { text: "xmax"; color: "#bdbdbd" }
                            SpinBox {
                                from: 0
                                to: Core.CalibrationViewCore.mappingImageWidth
                                value: modelData.xmax
                                onValueModified: Core.CalibrationViewCore.updateMappingObject(itemIndex, { xmax: value })
                            }
                            Label { text: "ymax"; color: "#bdbdbd" }
                            SpinBox {
                                from: 0
                                to: Core.CalibrationViewCore.mappingImageHeight
                                value: modelData.ymax
                                onValueModified: Core.CalibrationViewCore.updateMappingObject(itemIndex, { ymax: value })
                            }
                        }
                    }
                }
            }
        }
    }

    Button {
        Layout.fillWidth: true
        text: qsTr("保存标注 XML")
        enabled: Core.CalibrationViewCore.mappingObjects.length > 0
        onClicked: Core.CalibrationViewCore.saveCurrentMapping()
    }
}
