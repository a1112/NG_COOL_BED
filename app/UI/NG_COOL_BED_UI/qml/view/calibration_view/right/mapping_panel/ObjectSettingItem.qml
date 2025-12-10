import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core

Frame {
    id: root
    required property var modelData
    required property int index
    required property var directionOptions

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
                model: directionOptions
                currentIndex: {
                    const options = directionOptions
                    if (!options.indexOf) return -1
                    const idx = options.indexOf(modelData.direction)
                    return idx >= 0 ? idx : 0
                }
                onActivated: function(idx) {
                    Core.CalibrationViewCore.updateObjectSetting(index, "direction", directionOptions[idx])
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
                onValueModified: Core.CalibrationViewCore.updateObjectSetting(index, "width", value)
            }
            Label { text: "H"; color: "#b0bec5" }
            SpinBox {
                from: 0
                to: 10000
                value: modelData.height
                onValueModified: Core.CalibrationViewCore.updateObjectSetting(index, "height", value)
            }
        }
    }
}
