import QtQuick
import QtQuick.Controls
import "../../../core"
ItemDelegate {
    id: itemRoot
    width:  parent.width
     property int selectedIndex
    signal itemClicked(int index)
    implicitHeight: 30
    text: modelData.name
    checkable: true
    checked: index === selectedIndex
    onClicked: itemClicked(index)
    Rectangle{
        anchors.fill: parent
        visible: selectedIndex==index && CameraViewCore.selectedLayoutType==0
        color: "#00000000"
        border.color: "blue"
        border.width: 1
        }
}
