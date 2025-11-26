import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core

ColumnLayout {
    id: root
    spacing: 4

    Label {
        text: qsTr("相机图像")
        font.bold: true
        color: "#ffffff"
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.fillHeight: true
        radius: 4
        color: "#0d0d0d"

        Image {
            id: cameraImage
            anchors.fill: parent
            anchors.margins: 4
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            smooth: true
            cache: false
            source: Core.CalibrationViewCore.cameraImageSource
        }

        Label {
            anchors.centerIn: parent
            visible: cameraImage.status === Image.Null || !cameraImage.source
            text: qsTr("无图像")
            color: "#616161"
        }
    }
}
