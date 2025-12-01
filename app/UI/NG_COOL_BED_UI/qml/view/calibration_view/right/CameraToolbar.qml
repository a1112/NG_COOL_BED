import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
import "../../../base"

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
        ActionButton {
            text: qsTr("保存标注")
            onClicked: Core.CalibrationViewCore.saveLabelForCamera()
        }

    ActionButton {
        text: qsTr("从相机采图")
        enabled: !Core.CalibrationViewCore.offlineMode && Core.CalibrationViewCore.selectedCameraId.length > 0
        onClicked: Core.CalibrationViewCore.captureCurrentCamera()
    }

    ActionButton {
        text: qsTr("保存采集")
        onClicked: Core.CalibrationViewCore.saveCapturedImages()
    }

    ActionButton {
        text: qsTr("刷新透视")
        onClicked: Core.CalibrationViewCore.refreshPerspective()
    }

    CheckBox {
        text: qsTr("自动刷新")
        checked: Core.CalibrationViewCore.autoRefresh
        onToggled: Core.CalibrationViewCore.setAutoRefresh(checked)
    }
}
