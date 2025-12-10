import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Cores
import "left"
import "right"
import "dialogs"

Item {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true
    CreateFolderDialog {
        id: createFolderDialog
    }
    DeleteDialog{
            id: deleteDialog
    }


    Timer {
        interval: 6000
        repeat: true
        running: Cores.CalibrationViewCore.autoRefresh
        onTriggered: {
            Cores.CalibrationViewCore.refreshPerspective()
            Cores.CalibrationViewCore.refreshCameraImage()
        }
    }
    SplitView {
        anchors.fill: parent
        spacing: 10

        Frame {
            SplitView.preferredWidth: 360
            SplitView.fillHeight: true
            padding: 8
            background: Rectangle { color: "#151515"; radius: 4 }

            LeftPanel {
                anchors.fill: parent
                onAddRequested: createFolderDialog.openDialog()
                onDeleteRequested: function(folder) {
                    deleteDialog.folder = folder
                    deleteDialog.open()
                }
                onUseRequested: Cores.CalibrationViewCore.useFolder(folder)
            }
        }

        Frame {
            SplitView.fillWidth: true
            SplitView.fillHeight: true
            padding: 8
            background: Rectangle { color: "#0c0c0c"; radius: 4 }

            RightPanel {
                anchors.fill: parent
            }
        }
    }

    BusyIndicator {
        anchors.top: parent.top
        anchors.right: parent.right
        running: Cores.CalibrationViewCore.busy
        visible: running
    }
}
