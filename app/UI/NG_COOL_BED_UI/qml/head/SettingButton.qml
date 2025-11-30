import QtQuick
import QtQuick.Controls.Material

ItemDelegate {
    property alias iconSource: img.source

    Image {
        id: img
        anchors.fill: parent
        anchors.margins: 1
        source: ""
        fillMode: Image.PreserveAspectFit
    }
    background: Rectangle { color: "transparent" }
}
