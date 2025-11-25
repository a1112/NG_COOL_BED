import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Rectangle {
    Layout.fillWidth: true
    Layout.fillHeight: true
    color: "#101010"

    Column {
        anchors.centerIn: parent
        spacing: 6
        Label {
            text: qsTr("相机视图（待接入参考项目逻辑）")
            color: "white"
            font.pixelSize: 16
        }
        Label {
            text: qsTr("可在此按相机列表/分组呈现多路画面。")
            color: "#bbbbbb"
            font.pixelSize: 12
        }
    }
}
