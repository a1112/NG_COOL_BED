import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "../../../core"
Frame {
    id: root
    property var rows: []
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
        delegate: ItemDelegate {
            id:itd
            required property var modelData
            required property int index
            width: cameraList.width
            height: Math.max(34, contentRow.implicitHeight + 6)
            Rectangle{
                anchors.fill: parent
                visible:CameraViewCore.selectedLayoutType==1
                color: itd.ListView.isCurrentItem ? "#204a7a" : (mouseArea.containsMouse ? "#00000000" : "transparent")
                radius: 4
            }
            RowLayout {
                id: contentRow
                anchors.fill: parent
                anchors.margins: 6
                spacing: 8

                Label {
                    width: 150
                    font.pointSize: 13
                    text: (modelData.level === 0 ? modelData.display+"   冷床" : "└ " + modelData.display)
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
