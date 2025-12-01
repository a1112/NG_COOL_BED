import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "../../../core" as Core
import "../../../base"

Window {
    id: dialog
    property int itemIndex: -1
    readonly property var liveData: (itemIndex >= 0 && itemIndex < Core.CalibrationViewCore.mappingObjects.length)
                                    ? Core.CalibrationViewCore.mappingObjects[itemIndex]
                                    : ({})

    visible: false
    modality: Qt.NonModal
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
    color: "#f0f0f0"
    title: qsTr("编辑对象")
    width: 420
    height: 260

    function openFor(index) {
        itemIndex = index
        xminSpin.value = liveData.xmin || 0
        yminSpin.value = liveData.ymin || 0
        xmaxSpin.value = liveData.xmax || 0
        ymaxSpin.value = liveData.ymax || 0
        visible = true
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Label {
            text: qsTr("名称: %1").arg(liveData.name || "")
            font.pixelSize: 16
            font.bold: true
            color: "#202020"
        }

        GridLayout {
            columns: 2
            rowSpacing: 10
            columnSpacing: 12

            Label { text: "xmin"; color: "#444" }
            SpinBox {
                id: xminSpin
                from: 0
                to: Core.CalibrationViewCore.mappingImageWidth
                onValueChanged: if (dialog.itemIndex >= 0) Core.CalibrationViewCore.updateMappingObject(dialog.itemIndex, { xmin: value })
            }
            Label { text: "ymin"; color: "#444" }
            SpinBox {
                id: yminSpin
                from: 0
                to: Core.CalibrationViewCore.mappingImageHeight
                onValueChanged: if (dialog.itemIndex >= 0) Core.CalibrationViewCore.updateMappingObject(dialog.itemIndex, { ymin: value })
            }
            Label { text: "xmax"; color: "#444" }
            SpinBox {
                id: xmaxSpin
                from: 0
                to: Core.CalibrationViewCore.mappingImageWidth
                onValueChanged: if (dialog.itemIndex >= 0) Core.CalibrationViewCore.updateMappingObject(dialog.itemIndex, { xmax: value })
            }
            Label { text: "ymax"; color: "#444" }
            SpinBox {
                id: ymaxSpin
                from: 0
                to: Core.CalibrationViewCore.mappingImageHeight
                onValueChanged: if (dialog.itemIndex >= 0) Core.CalibrationViewCore.updateMappingObject(dialog.itemIndex, { ymax: value })
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Item { Layout.fillWidth: true }
            ActionButton {
                text: qsTr("关闭")
                onClicked: dialog.visible = false
            }
        }
    }
}
