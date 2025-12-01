import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../core" as Core
import "../../../../base"

RowLayout {
    id: root
    spacing: 8
    Label {
        text: qsTr("相机图像")
        font.bold: true
        color: "#ffffff"
    }
    Label {
        text: qsTr("缩放")
        color: "#b0bec5"
    }
    Slider {
        id: zoomSlider
        width: 200
        from: minZoom
        to: maxZoom
        value: zoomFactor
        onValueChanged: zoomFactor = value
    }
    Label {
        text: Math.round(zoomFactor * 100) + "%"
        color: "#9e9e9e"
        width: 50
        horizontalAlignment: Text.AlignHCenter
    }
    ActionButton {
        text: qsTr("重置")
        onClicked: zoomFactor = 1.0
    }

        Row {
            id: radioRow
            spacing: 4
            Repeater {
                model: Core.CalibrationViewCore.cameraRadioList
                delegate: RadioButton {
                    required property var modelData
                    text: modelData.label || modelData.camera
                    checked: Core.CalibrationViewCore.selectedCameraId === modelData.camera
                    onClicked: Core.CalibrationViewCore.selectedCameraId = modelData.camera
                }
            }
        }


    ActionButton {
        text: qsTr("从相机采图")
        enabled: !Core.CalibrationViewCore.offlineMode && Core.CalibrationViewCore.selectedCameraId.length > 0
        onClicked: Core.CalibrationViewCore.captureCurrentCamera()
    }

    ActionButton {
        visible: !Core.CalibrationViewCore.offlineMode && Core.CalibrationViewCore.selectedCameraId.length > 0
        text: qsTr("保存图像")
        onClicked: Core.CalibrationViewCore.saveCapturedImages()
    }
    Item{
        Layout.fillWidth: true


    }
    ActionButton {
        text: qsTr("保存全部标注")
        onClicked: Core.CalibrationViewCore.saveLabelForCamera()
    }
}
