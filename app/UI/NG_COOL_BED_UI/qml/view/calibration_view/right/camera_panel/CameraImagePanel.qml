import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../core" as Core
import "../../../../base"
import "../layers"

Item{
        id: root
    readonly property real baseWidth: Core.CalibrationViewCore.labelImageWidth || 1
    readonly property real baseHeight: Core.CalibrationViewCore.labelImageHeight || 1
    function requestRepaint(){
        return overlay.requestRepaint()
    }
    function adjustZoom(delta) {
        zoomFactor = Math.max(minZoom, Math.min(maxZoom, zoomFactor + delta))
        overlay.requestRepaint()
    }
ColumnLayout {
    anchors.fill: parent
    spacing: 6
    Flickable {
        id: scroller
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        contentWidth: baseWidth * zoomFactor
        contentHeight: baseHeight * zoomFactor
        ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

        Rectangle {
            id: canvas
            width: scroller.contentWidth
            height: scroller.contentHeight
            color: "#0d0d0d"
            radius: 4

            Image {
                id: cameraImage
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                asynchronous: true
                smooth: true
                cache: false
                source: Core.CalibrationViewCore.cameraImageSource
                sourceSize.width: baseWidth
                sourceSize.height: baseHeight

            }

            PolygonOverlay {
                id: overlay
                anchors.fill: parent
                shapes: Core.CalibrationViewCore.labelShapes
                scaleFactor: zoomFactor
                imageWidth: Core.CalibrationViewCore.labelImageWidth
                imageHeight: Core.CalibrationViewCore.labelImageHeight
                onPointMoved: function(shapeIndex, pointIndex, x, y) {
                    Core.CalibrationViewCore.updateLabelPoint(shapeIndex, pointIndex, x, y)
                }
                onPointMovedEnd: function(shapeIndex, pointIndex, x, y) {
                    Core.CalibrationViewCore.updateLabelPointEnd(shapeIndex, pointIndex, x, y)
                }
            }

            Label {
                anchors.centerIn: parent
                visible: cameraImage.status === Image.Null || !cameraImage.source
                text: qsTr("无图像")
                color: "#616161"
            }
            WheelHandler {
                acceptedModifiers: Qt.ControlModifier
                target: cameraImage
                onWheel: function(event) {
                    var delta = event.angleDelta.y / 1200
                    cip.adjustZoom(delta)
                    event.accepted = true
                }
            }
        }
    }
}

}
