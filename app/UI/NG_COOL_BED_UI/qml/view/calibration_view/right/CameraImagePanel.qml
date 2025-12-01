import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
import "../../../base"
import "./layers"

ColumnLayout {
    id: root
    spacing: 6
    function requestRepaint(){
        return overlay.requestRepaint()
    }
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
                    console.log("onPointMoved ",shapeIndex," ",pointIndex," ",x," ",y  )
                    Core.CalibrationViewCore.updateLabelPoint(shapeIndex, pointIndex, x, y)
                }
                onPointMovedEnd: function(shapeIndex, pointIndex, x, y) {
                    console.log("onPointMoved END ",shapeIndex," ",pointIndex," ",x," ",y  )
                    Core.CalibrationViewCore.updateLabelPoint(shapeIndex, pointIndex, x, y)
                }
            }

            Label {
                anchors.centerIn: parent
                visible: cameraImage.status === Image.Null || !cameraImage.source
                text: qsTr("无图像")
                color: "#616161"
            }
        }
    }
}
