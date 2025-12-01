import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."  // dialogs
import "../base"

Dialog {
    id: settingDialog
    property SettingCore core: settingCore

    modal: true
    focus: true
    x: (parent ? parent.width - width : 800) / 2
    y: (parent ? parent.height - height : 600) / 2
    standardButtons: Dialog.NoButton
    width: 520
    height: 640

    Rectangle {
        anchors.fill: parent
        color: "#1f1f1f"
        radius: 6
    }

    SettingCore {
        id: settingCore
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: qsTr("设置")
                font.pixelSize: 18
                font.bold: true
                color: "white"
            }
            Item { Layout.fillWidth: true }
            ActionButton {
                text: qsTr("关闭")
                onClicked: settingDialog.close()
            }
        }

        TabBar {
            id: tabs
            Layout.fillWidth: true
            TabButton { text: qsTr("常规") }
            TabButton { text: qsTr("测试") }
        }

        StackLayout {
            id: stack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabs.currentIndex

            GeneralSettingsPage {
                core: settingCore
            }

            TestingSettingsPage {
                core: settingCore
            }
        }
    }
}
