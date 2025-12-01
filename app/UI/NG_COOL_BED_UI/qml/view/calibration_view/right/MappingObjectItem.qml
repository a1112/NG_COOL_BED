import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core

Frame {
    id: root
    required property var modelData
    required property var index

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
                onValueModified: Core.CalibrationViewCore.updateMappingObject(index, { xmin: value })
            }
            Label { text: "ymin"; color: "#bdbdbd" }
            SpinBox {
                from: 0
                to: Core.CalibrationViewCore.mappingImageHeight
                value: modelData.ymin
                onValueModified: Core.CalibrationViewCore.updateMappingObject(index, { ymin: value })
            }
            Label { text: "xmax"; color: "#bdbdbd" }
            SpinBox {
                from: 0
                to: Core.CalibrationViewCore.mappingImageWidth
                value: modelData.xmax
                onValueModified: Core.CalibrationViewCore.updateMappingObject(index, { xmax: value })
            }
            Label { text: "ymax"; color: "#bdbdbd" }
            SpinBox {
                from: 0
                to: Core.CalibrationViewCore.mappingImageHeight
                value: modelData.ymax
                onValueModified: Core.CalibrationViewCore.updateMappingObject(index, { ymax: value })
            }
        }
    }
}
