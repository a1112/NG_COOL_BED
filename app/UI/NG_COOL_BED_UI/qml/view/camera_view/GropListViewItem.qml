import QtQuick
import QtQuick.Controls
ItemDelegate {
width: parent.width
required property var modelData
required property int index
text: modelData.name
checkable: true
checked: index === root.currentIndex
onClicked: {
    root.currentIndex = index
    root.selected(index)
}
}
