import QtQuick
import QtQuick.Controls.Material
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    Layout.fillWidth: true
    property var modelData: []
    property int currentIndex: 0
    signal selected(int index)

    spacing: 6

    Label {
        text: "分组布局"
        color: Material.color(Material.Blue)
        Layout.alignment:Qt.AlignHCenter
        font.bold: true
        font.pointSize: 20
    }

    ListView {
        id: list
        Layout.fillWidth: true
        height: contentHeight
        clip: true
        spacing: 4
        model: root.modelData
        delegate:GropListViewItem{

        }


    }
}
