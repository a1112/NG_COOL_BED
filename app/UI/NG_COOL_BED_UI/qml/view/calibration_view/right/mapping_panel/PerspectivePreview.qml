import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../core" as Core
import "../../../../base"
import "../../components"

ColumnLayout {
    id: root
    spacing: 6

    property real zoomFactor: 1.0
    property real minZoom: 0.5
    property real maxZoom: 3.0
    function adjustZoom(delta) {
        zoomFactor = Math.max(minZoom, Math.min(maxZoom, zoomFactor + delta))
    }

    MappingToolBar{
        id: toolbar
    }
    Flickable {
        id: scroller
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        contentWidth: canvas.imageWidth * zoomFactor
        contentHeight: canvas.imageHeight * zoomFactor
        ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

        Item {
            id: canvas
            property real imageWidth: 256
            property real imageHeight: 256
            width: imageWidth
            height: imageHeight
            scale: zoomFactor
            transformOrigin: Item.TopLeft

            WheelHandler {
                target: canvas
                                acceptedModifiers: Qt.ControlModifier
                onWheel: function(event) {
                    var delta = event.angleDelta.y / 1200
                    adjustZoom(delta)
                    event.accepted = true
                }
            }

            Rectangle {
                anchors.fill: parent
                color: "#0f0f0f"
                radius: 4
            }

            Image {
                id: previewImage
                anchors.centerIn: parent
                source: Core.CalibrationViewCore.perspectiveImageSource
                fillMode: Image.PreserveAspectFit
                cache: false
                asynchronous: true
                smooth: true
                onWidthChanged: {
                    if (status === Image.Ready && paintedWidth) {
                        canvas.imageWidth = paintedWidth
                        canvas.imageHeight = paintedHeight
                    }
                }
                onStatusChanged: {
                    if (status === Image.Ready && paintedWidth && paintedHeight) {
                        canvas.imageWidth = paintedWidth
                        canvas.imageHeight = paintedHeight
                    }
                }
                sourceSize.width: canvas.imageWidth
                sourceSize.height: canvas.imageHeight
            }

            Item {
                id: overlayLayer
                width: previewImage.status === Image.Ready ? previewImage.paintedWidth : canvas.imageWidth
                height: previewImage.status === Image.Ready ? previewImage.paintedHeight : canvas.imageHeight
                anchors.centerIn: previewImage
                visible: Core.CalibrationViewCore.mappingObjects.length > 0

                Repeater {
                    model: Core.CalibrationViewCore.mappingObjects
                    delegate: EditableRect {
                        objectIndex: index
                        boxData: modelData
                        canvasWidth: overlayLayer.width
                        canvasHeight: overlayLayer.height
                        imageWidth: Core.CalibrationViewCore.mappingImageWidth
                        imageHeight: Core.CalibrationViewCore.mappingImageHeight
                    }
                }
            }

            Label {
                anchors.centerIn: parent
                visible: !previewImage.source || previewImage.status === Image.Null
                text: qsTr("暂无透视图")
                color: "#5f6368"
            }
        }
    }
}
