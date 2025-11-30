import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core
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

    Dialog {
        id: deleteDialog
        modal: true
        title: qsTr("删除标注文件夹")
        standardButtons: Dialog.Cancel | Dialog.Ok
        property string folder: ""
        contentItem: Label {
            text: qsTr("确定删除 %1 ?").arg(deleteDialog.folder)
            color: "#ffffff"
        }
        onAccepted: Core.CalibrationViewCore.deleteFolder(folder)
    }

    Timer {
        interval: 6000
        repeat: true
        running: Core.CalibrationViewCore.autoRefresh
        onTriggered: {
            Core.CalibrationViewCore.refreshPerspective()
            Core.CalibrationViewCore.refreshCameraImage()
        }
    }

    Component.onCompleted: {
        if (typeof app_core !== "undefined") {
            Core.CalibrationViewCore.offlineMode = !!app_core.debug
        }
    }

    Connections {
        target: typeof app_core !== "undefined" ? app_core : null
        function onDebugChanged() {
            Core.CalibrationViewCore.offlineMode = !!app_core.debug
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
                onUseRequested: Core.CalibrationViewCore.useFolder(folder)
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
        running: Core.CalibrationViewCore.busy
        visible: running
    }
}
