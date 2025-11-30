import QtQuick

Rectangle {
    width: 15
    height: 15
    property bool has: false


    color: has?"red":"#000"
    border.width: 1
    border.color: "#22FFFFFF"
}
