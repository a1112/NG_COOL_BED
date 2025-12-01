import QtQuick
import QtQuick.Controls

Item {
    id: overlay
    property var shapes: []
    property real scaleFactor: 1.0
    property real imageWidth: 1
    property real imageHeight: 1
    signal pointMoved(int shapeIndex, int pointIndex, real x, real y)
    signal pointMovedEnd(int shapeIndex, int pointIndex, real x, real y)
    function requestRepaint() {
        polygonCanvas.requestPaint()
    }

    Canvas {
        id: polygonCanvas
        anchors.fill: parent
        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            ctx.clearRect(0, 0, width, height)
            var list = overlay.shapes || []
            list.forEach(function(shape) {
                var pts = shape.points || []
                if (pts.length < 2) return
                var color = shape.color || "#64b5f6"
                ctx.save()
                ctx.strokeStyle = color
                ctx.fillStyle = color + "33"
                ctx.lineWidth = 2
                ctx.beginPath()
                ctx.moveTo(pts[0][0] * overlay.scaleFactor, pts[0][1] * overlay.scaleFactor)
                for (var i = 1; i < pts.length; ++i) {
                    ctx.lineTo(pts[i][0] * overlay.scaleFactor, pts[i][1] * overlay.scaleFactor)
                }
                ctx.closePath()
                ctx.stroke()
                ctx.fill()
                ctx.restore()
            })
        }
    }

    Connections {
        target: overlay
        onShapesChanged: overlay.requestRepaint()
        onScaleFactorChanged: overlay.requestRepaint()
        onImageWidthChanged: overlay.requestRepaint()
        onImageHeightChanged: overlay.requestRepaint()
    }

    Repeater {
        model: overlay.shapes
        Item {
            required property int index
            required property var modelData
            readonly property int shapeIndex: index
            width: parent ? parent.width : 0
            height: parent ? parent.height : 0

            Repeater {
                model: modelData.points || []
                 Rectangle {
                     id:mv_rec
                    required property int index
                    readonly property var pt: modelData.points[index] || [0, 0]
                    width: 12
                    height: 12
                    radius: 6
                    color: "#ff9800"
                    border.color: "#ffa726"
                    border.width: 2
                    opacity: 0.9
                    x: (pt[0] * overlay.scaleFactor) - width / 2
                    y: (pt[1] * overlay.scaleFactor) - height / 2

                    DragHandler {
                        target: parent
                        xAxis.minimum: -parent.width / 2
                        xAxis.maximum: overlay.width - parent.width / 2
                        yAxis.minimum: -parent.height / 2
                        yAxis.maximum: overlay.height - parent.height / 2
                        cursorShape: active ? Qt.ClosedHandCursor : Qt.OpenHandCursor
                        onTranslationChanged: {
                            var newX = (parent.x + parent.width / 2) / overlay.scaleFactor
                            var newY = (parent.y + parent.height / 2) / overlay.scaleFactor
                            newX = Math.max(0, Math.min(overlay.imageWidth, newX))
                            newY = Math.max(0, Math.min(overlay.imageHeight, newY))
                            overlay.pointMoved(shapeIndex, index, newX, newY)
                            overlay.requestRepaint()
                        }
                        onActiveChanged: {
                            if (!active) {
                                var newX = (parent.x + parent.width / 2) / overlay.scaleFactor
                                var newY = (parent.y + parent.height / 2) / overlay.scaleFactor
                                newX = Math.max(0, Math.min(overlay.imageWidth, newX))
                                newY = Math.max(0, Math.min(overlay.imageHeight, newY))
                                overlay.pointMovedEnd(shapeIndex, index, newX, newY)

                                mv_rec.x = Qt.binding(()=>{return (pt[0] * overlay.scaleFactor) - width / 2})
                                mv_rec.y = Qt.binding(()=>{return (pt[1] * overlay.scaleFactor) - height / 2})

                            }
                        }
                    }
                }
            }
        }
    }
}
