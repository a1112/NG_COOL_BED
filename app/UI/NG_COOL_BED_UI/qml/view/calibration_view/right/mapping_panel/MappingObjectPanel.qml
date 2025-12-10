import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../../core" as Core
import "../../../../base"



ColumnLayout {
    id: root
    spacing: 6

    Label {
        text: qsTr("对象设置（XML）")
        font.bold: true
        color: "#ffffff"
    }

    ScrollView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 8

            Repeater {
                model: Core.CalibrationViewCore.mappingObjects

                delegate: ItemDelegate {
                    required property int index
                    required property var modelData
                    width: parent.width

                    readonly property var liveData: (Core.CalibrationViewCore.mappingObjects[index] || modelData || {})
                    text: liveData.name + "  |  x1:" + liveData.xmin + "  y1:" + liveData.ymin +
                          "  x2:" + liveData.xmax + "  y2:" + liveData.ymax

                    onClicked: editDialog.openFor(index)
                }
            }
        }
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: 10
        ActionButton {
            text: qsTr("刷新")
            onClicked: Core.CalibrationViewCore.loadMappingForGroup()
        }
        ActionButton {
            text: qsTr("保存")
            enabled: Core.CalibrationViewCore.mappingObjects.length > 0
            onClicked: Core.CalibrationViewCore.saveCurrentMapping()
        }
    }

    MappingObjectEditDialog {
        id: editDialog
    }
}
