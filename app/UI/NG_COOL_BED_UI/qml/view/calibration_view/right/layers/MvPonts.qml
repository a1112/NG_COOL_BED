import QtQuick

Item {
    required property int index
    required property var modelData
    property int shapeIndex: index
    width: parent ? parent.width : 0
    height: parent ? parent.height : 0
    Repeater {
        model: modelData.points || []
        MvPoint{}
    }
}
