import QtQuick
import QtQuick.Controls.Material
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
ColumnLayout {
    id: root
    Layout.fillWidth: true
    spacing: 6
    Label {
        text: "分组布局"
        color: Material.color(Material.Blue)
        Layout.alignment: Qt.AlignHCenter
        font.bold: true
        font.pointSize: 20
    }
    ListView {
        id: list
        Layout.fillWidth: true
        implicitHeight: contentHeight
        clip: true
        spacing: 4
        model: Core.CameraViewCore.layoutConfigs ? Core.CameraViewCore.layoutConfigs : []
        currentIndex:  Core.CameraViewCore.selectedLayoutIndex
        onCurrentIndexChanged: Core.CameraViewCore.selectedLayoutIndex = currentIndex

        delegate: GropListViewItem {
            selectedIndex: Core.CameraViewCore.selectedLayoutIndex
            onItemClicked: function(idx) {
                list.currentIndex = idx
                Core.CameraViewCore.selectedLayoutType = 0
                Core.CameraViewCore.selectedLayoutIndex = idx
            }
        }
    }
}
