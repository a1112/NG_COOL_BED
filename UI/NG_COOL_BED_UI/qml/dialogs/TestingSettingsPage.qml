import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: testPage
    property var core: null

    property QtObject coreRef: core

    spacing: 8
    anchors.fill: parent

    GroupBox {
        title: qsTr("测试数据")
        Layout.fillWidth: true
        ColumnLayout {
            spacing: layoutSpacing
            Layout.fillWidth: true

            RowLayout {
                spacing: 6
                Layout.fillWidth: true
                Label { text: qsTr("数据文件夹"); Layout.preferredWidth: 90 }
                TextField {
                    Layout.fillWidth: true
                    text: coreRef ? coreRef.testDataFolder : ""
                    onEditingFinished: if (coreRef) coreRef.testDataFolder = text
                }
            }
        }
    }

    Item { Layout.fillHeight: true }
}
