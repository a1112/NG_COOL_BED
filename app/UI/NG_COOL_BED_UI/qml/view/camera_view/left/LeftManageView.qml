import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."
import "../../../core" as Core

ColumnLayout {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true
    spacing: 8

    GropListView {
    }

    Label {
        text: "相机列表"
        color: "green"
        font.bold: true
        Layout.alignment: Qt.AlignHCenter
        font.pointSize: 20
    }

    IpTreeView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        rows: Core.CameraViewCore.flatTreeRows
        onRowClicked: function(rowData) {
            if (rowData && rowData.level === 1 && rowData.seq !== undefined && rowData.seq !== null) {
                Core.CameraViewCore.selectedSlotNumber = rowData.seq
                const idx = Core.CameraViewCore.layoutIndexForSlot(rowData.seq)
                if (idx >= 0) Core.CameraViewCore.selectedLayoutIndex = idx
                Core.CameraViewCore.selectedLayoutType = 1
            } else {
                Core.CameraViewCore.selectedSlotNumber = 0
            }
        }
    }
}
