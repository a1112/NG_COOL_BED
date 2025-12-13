import QtQuick
import QtQuick.Controls.Material
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
ColumnLayout {
    id: root
    Layout.fillWidth: true
    spacing: 6
    ComboBox {
        id: imageSourceSelector
        Layout.fillWidth: true
        font.pointSize: 14
        model: Core.CameraViewCore.imageSourceOptions
        textRole: "label"
        currentIndex: {
            const idx = Core.CameraViewCore.imageSourceIndex()
            return idx >= 0 ? idx : 0
        }
        onActivated: function(index) {
            const options = Core.CameraViewCore.imageSourceOptions || []
            if (!options.length)
                return
            const option = options[index] || options[0]
            if (option && option.key)
                Core.CameraViewCore.selectedImageSourceKey = option.key
        }
    }
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
