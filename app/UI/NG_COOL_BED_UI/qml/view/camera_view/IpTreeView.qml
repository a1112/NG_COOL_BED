import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Frame {
    id: root
    property var rows: []
    // 当前选中索引，向外暴露
    property alias currentIndex: cameraList.currentIndex
    signal rowClicked(var rowData)

    Layout.fillWidth: true
    Layout.fillHeight: true
    padding: 0
    background: Rectangle { color: "#1a1a1a"; radius: 4 }

    ListView {
        id: cameraList
        anchors.fill: parent
        model: root.rows
        clip: true
        spacing: 2
        boundsBehavior: Flickable.StopAtBounds
        focus: true
        currentIndex: -1
        ScrollBar.vertical: ScrollBar {}
        highlightMoveDuration: 120
        highlightResizeDuration: 120

        delegate: Rectangle {
            required property var modelData
            required property int index
            width: cameraList.width
            height: Math.max(34, contentRow.implicitHeight + 6)
            color: ListView.isCurrentItem ? "#204a7a" : (mouseArea.containsMouse ? "#222222" : "transparent")
            radius: 4

            RowLayout {
                id: contentRow
                anchors.fill: parent
                anchors.margins: 6
                spacing: 8

                Label {
                    width: 150
                    text: (modelData.level === 0 ? modelData.display : "└ " + modelData.display)
                    leftPadding: modelData.level * 16
                    color: modelData.level === 0 ? "#fff" : "#e0e0e0"
                    font.bold: modelData.level === 0
                    elide: Text.ElideRight
                }
                Label {
                    width: 110
                    text: modelData.ip
                    color: "#9e9e9e"
                    elide: Text.ElideRight
                }
                Label {
                    width: 48
                    text: modelData.seq ? ("#" + modelData.seq) : ""
                    color: "#8bc34a"
                }
                Label {
                    text: modelData.position || ""
                    color: "#9e9e9e"
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
            }

            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    cameraList.currentIndex = index
                    root.rowClicked(modelData)
                }
            }
        }
    }
}
