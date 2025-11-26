import QtQuick
import QtQuick.Controls
import "../../core" as CoreModule

Item {
    id: root
    property int objectIndex: -1
    property var boxData: ({})
    property real imageWidth: 1
    property real imageHeight: 1
    property real canvasWidth: 1
    property real canvasHeight: 1
    property color accent: (boxData && boxData.color) ? boxData.color : "#ff9800"
    readonly property real minSize: 12
    property bool dragging: false
    property string title: (boxData && boxData.name) ? boxData.name : ""

    function syncFromBox() {
        if (!boxData || dragging) return
        if (canvasWidth <= 0 || canvasHeight <= 0) return
        const sx = canvasWidth / Math.max(imageWidth, 1)
        const sy = canvasHeight / Math.max(imageHeight, 1)
        const w = Math.max(minSize, Math.abs((boxData.xmax - boxData.xmin) * sx))
        const h = Math.max(minSize, Math.abs((boxData.ymax - boxData.ymin) * sy))
        root.width = w
        root.height = h
        root.x = Math.min(Math.max(0, (boxData.xmin || 0) * sx), Math.max(0, canvasWidth - w))
        root.y = Math.min(Math.max(0, (boxData.ymin || 0) * sy), Math.max(0, canvasHeight - h))
    }

    function commitBox() {
        if (!boxData) return
        const sx = canvasWidth / Math.max(imageWidth, 1)
        const sy = canvasHeight / Math.max(imageHeight, 1)
        const invX = sx !== 0 ? 1 / sx : 0
        const invY = sy !== 0 ? 1 / sy : 0
        CoreModule.CalibrationViewCore.updateMappingObject(objectIndex, {
                                                             xmin: root.x * invX,
                                                             ymin: root.y * invY,
                                                             xmax: (root.x + root.width) * invX,
                                                             ymax: (root.y + root.height) * invY
                                                         })
    }

    onBoxDataChanged: syncFromBox()
    onCanvasWidthChanged: syncFromBox()
    onCanvasHeightChanged: syncFromBox()
    onImageWidthChanged: syncFromBox()
    onImageHeightChanged: syncFromBox()

    Rectangle {
        anchors.fill: parent
        color: accent
        opacity: 0.18
        radius: 2
    }

    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.color: accent
        border.width: 2
        radius: 2
    }

    Text {
        id: titleText
        text: title
        color: "white"
        font.bold: true
        font.pixelSize: 14
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 4
        visible: title.length > 0
    }

    MouseArea {
        anchors.fill: parent
        drag.target: root
        drag.minimumX: 0
        drag.minimumY: 0
        drag.maximumX: Math.max(0, root.canvasWidth - root.width)
        drag.maximumY: Math.max(0, root.canvasHeight - root.height)
        cursorShape: Qt.OpenHandCursor
        onPressed: {
            cursorShape = Qt.ClosedHandCursor
            root.dragging = true
        }
        onReleased: {
            cursorShape = Qt.OpenHandCursor
            root.dragging = false
            root.commitBox()
        }
    }
}
