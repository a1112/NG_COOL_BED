import QtQuick

Image {
    id: root
    property alias sourcePath: root.source
    asynchronous: true
    fillMode: Image.PreserveAspectFit
    cache: false
    source: ""
}
