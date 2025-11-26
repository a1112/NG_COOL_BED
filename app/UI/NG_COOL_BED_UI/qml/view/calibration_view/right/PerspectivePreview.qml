import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core
import "../components"

ColumnLayout {
    id: root
    spacing: 4

    Label {
        text: qsTr("透视图像")
        font.bold: true
        color: "#ffffff"
    }

    Item {
        id: canvas
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true

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
            sourceSize.width: canvas.width
            sourceSize.height: canvas.height
        }

        Item {
            id: overlayLayer
            width: previewImage.status === Image.Ready ? previewImage.paintedWidth : canvas.width
            height: previewImage.status === Image.Ready ? previewImage.paintedHeight : canvas.height
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
