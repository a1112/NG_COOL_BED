import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../base"

Dialog {
    id: root
    modal: true
    focus: true
    standardButtons: Dialog.NoButton
    width: 460
    height: 260

    property string hostText: ""
    property string portText: ""

    function openDialog() {
        hostText = (app_api && app_api.server_url) ? (app_api.server_url.server_ip || "") : ""
        portText = (app_api && app_api.server_url) ? ("" + (app_api.server_url.server_port || "")) : ""
        open()
    }

    function apply() {
        if (!app_api || !app_api.server_url)
            return
        var host = (hostText || "").trim()
        var port = parseInt(portText, 10)
        if (!host.length)
            return
        if (!Number.isFinite(port) || port <= 0 || port > 65535)
            return
        app_api.server_url.server_ip = host
        app_api.server_url.server_port = port
        if (app_core && app_core.flush)
            app_core.flush()
        close()
    }

    Rectangle {
        anchors.fill: parent
        color: "#1f1f1f"
        radius: 6
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: qsTr("IP 设置")
                font.pixelSize: 18
                font.bold: true
                color: "white"
            }
            Item { Layout.fillWidth: true }
            ActionButton {
                text: qsTr("关闭")
                onClicked: root.close()
            }
        }

        GroupBox {
            title: qsTr("后端 API 地址")
            Layout.fillWidth: true
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    Label { text: qsTr("Host"); Layout.preferredWidth: 70 }
                    TextField {
                        Layout.fillWidth: true
                        placeholderText: "127.0.0.1"
                        text: root.hostText
                        onTextChanged: root.hostText = text
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Label { text: qsTr("Port"); Layout.preferredWidth: 70 }
                    TextField {
                        Layout.fillWidth: true
                        placeholderText: "8001"
                        inputMethodHints: Qt.ImhDigitsOnly
                        text: root.portText
                        onTextChanged: root.portText = text
                    }
                }

                Label {
                    Layout.fillWidth: true
                    color: "#b0b0b0"
                    text: (app_api && app_api.server_url) ? ("当前: " + app_api.server_url.serverUrl) : ""
                    elide: Text.ElideRight
                }
            }
        }

        Item { Layout.fillHeight: true }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            ActionButton {
                text: qsTr("应用")
                onClicked: root.apply()
            }
        }
    }
}

