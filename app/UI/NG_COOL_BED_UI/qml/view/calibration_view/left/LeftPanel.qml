import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
import "."

ColumnLayout {
    id: root
    signal addRequested()
    signal deleteRequested(string folder)
    signal useRequested(string folder)

    spacing: 8

    FolderToolbar {
        Layout.fillWidth: true
        onAddRequested: root.addRequested()
        onDeleteRequested: root.deleteRequested(folder)
        onUseRequested: root.useRequested(folder)
    }

    GroupListPanel {
        Layout.fillWidth: true
        Layout.fillHeight: true
    }

    Label {
        Layout.fillWidth: true
        text: Core.CalibrationViewCore.statusMessage
        color: "#64b5f6"
        wrapMode: Text.WordWrap
    }
}
