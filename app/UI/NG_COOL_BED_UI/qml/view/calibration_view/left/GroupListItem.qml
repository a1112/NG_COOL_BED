import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core

ItemDelegate {
    required property var modelData
    Layout.fillWidth: true
    checkable: true
    width: parent.width
    checked: Core.CalibrationViewCore.selectedGroupKey === modelData.key
    onClicked: Core.CalibrationViewCore.selectedGroupKey = modelData.key

    background: Rectangle {
        anchors.fill: parent
        color: checked ? "#1e88e5" : "#111"
        border.color: checked ? "#90caf9" : "#222"
        radius: 8
    }
    contentItem: ColumnLayout {
        id: col
        anchors.fill: parent
        anchors.margins: 8
        spacing: 6

        ColumnLayout {
            spacing: 4
            Layout.fillWidth: true

            RowLayout {
                spacing: 10
                Layout.fillWidth: true
                Label {
                    text: qsTr("组名称: ") + modelData.key
                    font.pixelSize: 16
                    font.bold: true
                    color: checked ? "#ffffff" : "#e0e0e0"
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
                Label {
                    text: qsTr("优先级 %1").arg(modelData.priority)
                    color: checked ? "#bbdefb" : "#bbbbbb"
                    font.pixelSize: 13
                }
                Label {
                    text: qsTr("相机 %1").arg(modelData.cameraList.length)
                    color: checked ? "#bbdefb" : "#bbbbbb"
                    font.pixelSize: 13
                }
            }

            Label {
                text: qsTr("描述：%1").arg(modelData.msg || "")
                color: checked ? "#f0f4ff" : "#d0d0d0"
                wrapMode: Text.WordWrap
                font.pixelSize: 14
                Layout.fillWidth: true
            }
        }
        Flow {
            Layout.fillWidth: true
            spacing: 4
            Repeater {
                model: modelData.cameraList
                delegate: Rectangle {
                    implicitWidth: chipText.implicitWidth + 16
                    implicitHeight: 24
                    radius: 12
                    color: checked ? "#3f51b5" : "#222"
                    Text {
                        id: chipText
                        anchors.fill: parent
                        anchors.margins: 2
                        text: modelData.camera
                        color: "#fafafa"
                        font.pixelSize: 12
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
    }
}

