import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: page
    property var core: null
    property QtObject coreRef: core
    spacing: 8
    anchors.fill: parent

    GroupBox {
        title: qsTr("基础")
        Layout.fillWidth: true
        ColumnLayout {
            spacing: 5
            Layout.fillWidth: true

            RowLayout {
                spacing: 6
                Layout.fillWidth: true
                Label { text: qsTr("URL"); Layout.preferredWidth: 90 }
                TextField {
                    Layout.fillWidth: true
                    text: coreRef ? coreRef.serverUrl : ""
                    onEditingFinished: if (coreRef) coreRef.serverUrl = text
                }
            }

            RowLayout {
                spacing: 6
                Layout.fillWidth: true
                Label { text: qsTr("IP"); Layout.preferredWidth: 90 }
                TextField {
                    Layout.fillWidth: true
                    text: coreRef ? coreRef.ipAddress : ""
                    onEditingFinished: if (coreRef) coreRef.ipAddress = text
                }
            }

            RowLayout {
                spacing: 6
                Layout.fillWidth: true
                Label { text: qsTr("模型类型"); Layout.preferredWidth: 90 }
                TextField {
                    Layout.fillWidth: true
                    text: coreRef ? coreRef.modelType : ""
                    onEditingFinished: if (coreRef) coreRef.modelType = text
                }
            }
        }
    }

    GroupBox {
        title: qsTr("配置")
        Layout.fillWidth: true
        ColumnLayout {
            spacing: 5
            Layout.fillWidth: true

            RowLayout {
                spacing: 6
                Layout.fillWidth: true
                Label { text: qsTr("配置文件路径"); Layout.preferredWidth: 90 }
                TextField {
                    Layout.fillWidth: true
                    text: coreRef ? coreRef.configPath : ""
                    onEditingFinished: if (coreRef) coreRef.configPath = text
                }
            }

            RowLayout {
                spacing: 6
                Layout.fillWidth: true
                Label { text: qsTr("当前配置"); Layout.preferredWidth: 90 }
                TextField {
                    Layout.fillWidth: true
                    text: coreRef ? coreRef.currentConfig : ""
                    onEditingFinished: if (coreRef) coreRef.currentConfig = text
                }
            }
        }
    }

    GroupBox {
        title: qsTr("模型选择")
        Layout.fillWidth: true
        ColumnLayout {
            spacing: 5
            Layout.fillWidth: true

            RowLayout {
                spacing: 6
                Layout.fillWidth: true
                Label { text: qsTr("类型"); Layout.preferredWidth: 90 }
                ComboBox {
                    Layout.fillWidth: true
                    model: coreRef ? coreRef.modelCategories : []
                    currentIndex: coreRef && coreRef.modelCategories ? coreRef.modelCategories.indexOf(coreRef.selectedCategory) : 0
                    onCurrentTextChanged: if (coreRef) {
                        coreRef.selectedCategory = currentText
                        if (currentText === "目标检测" && coreRef.modelListDet.length > 0) {
                            coreRef.selectedModel = coreRef.modelListDet[0]
                        } else if (currentText === "分割" && coreRef.modelListSeg.length > 0) {
                            coreRef.selectedModel = coreRef.modelListSeg[0]
                        }
                    }
                }
            }

            RowLayout {
                spacing: 6
                Layout.fillWidth: true
                Label { text: qsTr("模型"); Layout.preferredWidth: 90 }
                ComboBox {
                    Layout.fillWidth: true
                    model: coreRef
                           ? (coreRef.selectedCategory === "分割" ? coreRef.modelListSeg : coreRef.modelListDet)
                           : []
                    currentIndex: coreRef
                                  ? ((coreRef.selectedCategory === "分割"
                                      ? coreRef.modelListSeg.indexOf(coreRef.selectedModel)
                                      : coreRef.modelListDet.indexOf(coreRef.selectedModel)))
                                  : 0
                    onCurrentTextChanged: if (coreRef) coreRef.selectedModel = currentText
                }
            }
        }
    }

    Item { Layout.fillHeight: true }
}
