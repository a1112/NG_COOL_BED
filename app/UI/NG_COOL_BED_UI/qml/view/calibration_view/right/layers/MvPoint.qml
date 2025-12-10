import QtQuick

Rectangle {
    required property int index
    readonly property var pt: modelData.points[index] || [0, 0]
    width: 18
    height: 18
    radius: 9
    color: "#ff9800"
    border.color: "#ffa726"
    border.width: 2
    opacity: 0.9
    x: (pt[0] * overlay.scaleFactor) - width / 2
    y: (pt[1] * overlay.scaleFactor) - height / 2
    property bool ready: false

    function commitPosition() {
        if (!ready) return
        var newX = (x + width / 2) / overlay.scaleFactor
        var newY = (y + height / 2) / overlay.scaleFactor
        newX = Math.max(0, Math.min(overlay.imageWidth, newX))
        newY = Math.max(0, Math.min(overlay.imageHeight, newY))
        overlay.pointMoved(shapeIndex, index, newX, newY)
        // requestPaint()
    }
    onXChanged: commitPosition()
    onYChanged: commitPosition()
    Component.onCompleted: ready = true

    DragHandler {
        target: parent
        xAxis.minimum: -parent.width / 2
        xAxis.maximum: overlay.width - parent.width / 2
        yAxis.minimum: -parent.height / 2
        yAxis.maximum: overlay.height - parent.height / 2
        cursorShape: active ? Qt.ClosedHandCursor : Qt.OpenHandCursor
    }
}

