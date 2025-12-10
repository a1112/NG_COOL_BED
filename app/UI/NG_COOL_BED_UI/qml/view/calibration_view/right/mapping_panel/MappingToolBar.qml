import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../core" as Core
import "../../../../base"
import "../../components"

RowLayout {
    spacing: 8
    Layout.fillWidth: true
    Label {
        text: qsTr("透视图像")
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
