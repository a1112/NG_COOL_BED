import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Column {
    required property var modelData
    width: root.width
    spacing: 4

    Label {
        text: qsTr("组别 %1").arg(modelData.lineKey)
        font.pointSize: 18
        font.bold: true
        color: "#9bd8ff"
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Repeater {
        model: modelData.groupList
        GroupListItem{}

    }
}
