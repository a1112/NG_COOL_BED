import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../core" as Core
import "../../../../base"

RowLayout {
    id: root
    spacing: 8
    function isLocalHost() {
        return app_api && app_api.server_url &&
                (app_api.server_url.hostname === "127.0.0.1" || app_api.server_url.hostname === "localhost")
    }
    function labelFileUrl() {
        if (!Core.CalibrationViewCore.currentFolder || !Core.CalibrationViewCore.selectedCameraId)
            return ""
        return Qt.resolvedUrl("../../../../../config/calibrate/cameras/" +
                              Core.CalibrationViewCore.currentFolder + "/" +
                              Core.CalibrationViewCore.selectedCameraId + ".json")
    }
    function openLabelFolder() {
        if (!isLocalHost())
            return
        var fileUrl = labelFileUrl()
        if (!fileUrl || !fileUrl.length)
            return
        var normalized = fileUrl
        if (normalized.startsWith("qrc:")) {
            // 无法从 qrc 打开本地目录
            return
        }
        if (!normalized.startsWith("file:"))
            normalized = "file:///" + normalized
        var slash = normalized.lastIndexOf("/")
        if (slash > 0)
            normalized = normalized.substring(0, slash)
        Qt.openUrlExternally(normalized)
    }
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
    ActionButton {
        text: qsTr("位置")
        visible: isLocalHost()
        onClicked: openLabelFolder()
    }
}
