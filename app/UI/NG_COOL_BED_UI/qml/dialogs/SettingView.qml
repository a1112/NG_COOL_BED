import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."  // dialogs
import "../base"

Dialog {
    id: settingDialog
    property SettingCore core: settingCore
    property bool predictDisplayEnabled: true
    property bool predictDisplayBusy: false
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

    function refreshPredictDisplay() {
        if (!app_api || !app_api.get_predict_display)
            return
        predictDisplayBusy = true
        app_api.get_predict_display(
                    function(resp) {
                        predictDisplayEnabled = !!(resp && resp.enable)
                        predictDisplayBusy = false
                    },
                    function(err) {
                        console.warn("get_predict_display error", err)
                        predictDisplayBusy = false
                    })
    }

    function setPredictDisplay(enable) {
        if (!app_api || !app_api.set_predict_display)
            return
        predictDisplayBusy = true
        app_api.set_predict_display(
                    enable,
                    function(resp) {
                        predictDisplayEnabled = !!(resp && resp.enable)
                        predictDisplayBusy = false
                    },
                    function(err) {
                        console.warn("set_predict_display error", err)
                        predictDisplayBusy = false
                    })
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 2
        spacing: 1
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
                anchors.fill: parent
                core: settingCore
            }

            TestingSettingsPage {
                core: settingCore
            }
        }

        GroupBox {
            title: qsTr("显示")
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                CheckDelegate {
                    Layout.preferredWidth: 200
                    text: qsTr("显示算法调试窗口")
                    checked: predictDisplayEnabled
                    enabled: !predictDisplayBusy
                    onClicked: settingDialog.setPredictDisplay(checked)
                }
                Item { Layout.fillWidth: true }
                BusyIndicator {
                    running: predictDisplayBusy
                    visible: predictDisplayBusy
                    width: 24
                    height: 24
                }
            }
        }
    }

    Component.onCompleted: refreshPredictDisplay()
}
