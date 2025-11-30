import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core

RowLayout {
    id: root
    spacing: 8

    Flickable {
        Layout.fillWidth: true
        Layout.preferredHeight: 36
        clip: true
        contentWidth: radioRow.implicitWidth
        contentHeight: radioRow.implicitHeight
        interactive: radioRow.implicitWidth > width
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
    }

    Button {
        text: qsTr("从相机采图")
        enabled: !Core.CalibrationViewCore.offlineMode && Core.CalibrationViewCore.selectedCameraId.length > 0
        onClicked: Core.CalibrationViewCore.captureCurrentCamera()
    }

    Button {
        text: qsTr("保存采集")
        onClicked: Core.CalibrationViewCore.saveCapturedImages()
    }

    Button {
        text: qsTr("刷新透视")
        onClicked: Core.CalibrationViewCore.refreshPerspective()
    }

    CheckBox {
        text: qsTr("自动刷新")
        checked: Core.CalibrationViewCore.autoRefresh
        onToggled: Core.CalibrationViewCore.setAutoRefresh(checked)
    }
}
