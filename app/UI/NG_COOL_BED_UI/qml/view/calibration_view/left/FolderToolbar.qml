import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
import "../../../base"

ColumnLayout {
    id: root
    property alias folderCombo: folderCombo
    signal addRequested()
    signal deleteRequested(string folder)
    signal useRequested(string folder)

    ComboBox {
        Layout.fillWidth: true
        id: folderCombo
        implicitHeight: 35
        model: Core.CalibrationViewCore.folderList
        textRole: ""
        currentIndex: {
            const list = Core.CalibrationViewCore.folderList || []
            if (!list.indexOf) return -1
            const idx = list.indexOf(Core.CalibrationViewCore.currentFolder)
            return idx >= 0 ? idx : -1
        }
        displayText: currentText
        // currentText: {
        //     const current = Core.CalibrationViewCore.currentFolder
        //     return current && current.length ? current : qsTr("未选择")
        // }
        onActivated: function(index) {
            const list = Core.CalibrationViewCore.folderList || []
            const name = list[index] || ""
            if (name && Core.CalibrationViewCore.currentFolder !== name) {
                Core.CalibrationViewCore.currentFolder = name
            }
        }
        contentItem: Text {
            text: folderCombo.currentText
            color: "white"
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        delegate: ItemDelegate {
            width: folderCombo.width
            text: modelData
            onClicked: folderCombo.currentIndex = index
        }
    }
    RowLayout{
    Layout.fillWidth: true
    ActionButton {
        text: qsTr("添加")
        onClicked: root.addRequested()
    }

    ActionButton {
        text: qsTr("删除")
        enabled: Core.CalibrationViewCore.currentFolder.length > 0
        onClicked: root.deleteRequested(Core.CalibrationViewCore.currentFolder)
    }

    ActionButton {
        text: qsTr("设置")
        enabled: Core.CalibrationViewCore.currentFolder.length > 0
        onClicked: root.useRequested(Core.CalibrationViewCore.currentFolder)
    }
    ActionButton {
        text: qsTr("位置")

    }


    }
}
