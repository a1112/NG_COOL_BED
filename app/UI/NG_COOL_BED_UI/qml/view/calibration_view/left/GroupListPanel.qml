import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core

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
            LineGroupItem{
            }
        }
    }
}
