import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {

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
