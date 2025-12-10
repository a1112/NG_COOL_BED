import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
import "../../../base"

Dialog {
    id: dialog
    modal: true
    focus: true
    title: qsTr("添加标注文件夹")
    standardButtons: Dialog.Cancel

    property string folderName: ""
    property string templateName: Core.CalibrationViewCore.currentFolder
    property string sourceMode: "copy"
    property string errorText: ""

    function openDialog() {
        folderName = ""
        templateName = Core.CalibrationViewCore.currentFolder
        sourceMode = "copy"
        errorText = ""
        open()
    }

    contentItem: ColumnLayout {
        spacing: 12
        Label {
            text: qsTr("名称")
            color: "#ffffff"
        }
        TextField {
            Layout.fillWidth: true
            text: dialog.folderName
            placeholderText: qsTr("例如 calibrate_202412")
            onTextChanged: {
                dialog.folderName = text.trim()
                dialog.errorText = ""
            }
        }

        Label {
            text: qsTr("模板")
            color: "#ffffff"
        }
        ComboBox {
            Layout.fillWidth: true
            model: Core.CalibrationViewCore.folderList
            currentIndex: {
                const list = Core.CalibrationViewCore.folderList || []
                if (!list.indexOf) return -1
                const idx = list.indexOf(dialog.templateName)
                return idx >= 0 ? idx : -1
            }
            onActivated: function(idx) {
                const list = Core.CalibrationViewCore.folderList || []
                dialog.templateName = list[idx] || ""
            }
        }

        Label {
            text: qsTr("图像来源")
            color: "#ffffff"
        }
        RowLayout {
            spacing: 16
            RadioButton {
                text: qsTr("拷贝")
                checked: dialog.sourceMode === "copy"
                onClicked: dialog.sourceMode = "copy"
            }
            RadioButton {
                text: qsTr("从相机获取")
                checked: dialog.sourceMode === "camera"
                enabled: !Core.CalibrationViewCore.offlineMode
                onClicked: dialog.sourceMode = "camera"
            }
        }

        Label {
            text: dialog.errorText
            color: "#ff8a65"
            visible: dialog.errorText.length > 0
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Item { Layout.fillWidth: true }
            ActionButton {
                text: qsTr("确认")
                enabled: dialog.folderName.length > 0
                onClicked: dialog.apply()
            }
        }
    }

    function apply() {
        if (!folderName || folderName.length === 0) {
            errorText = qsTr("请输入名称")
            return
        }
        const list = Core.CalibrationViewCore.folderList || []
        const exists = list.some ? list.some((item)=> item.toLowerCase() === folderName.toLowerCase()) :
                                   (list.indexOf && list.indexOf(folderName) !== -1)
        if (exists) {
            errorText = qsTr("名称重复")
            return
        }
        Core.CalibrationViewCore.createFolder({
                                                  name: folderName,
                                                  template: templateName,
                                                  mode: sourceMode
                                              },
                                              function(success){
                                                  if (success) dialog.close()
                                              })
    }
}
