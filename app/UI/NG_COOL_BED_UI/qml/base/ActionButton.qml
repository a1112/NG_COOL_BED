import QtQuick
import QtQuick.Controls

// 统一风格的操作按钮
Button {
    id: control

    property bool danger: false
    property bool active: false
    property color accentColor: "#4fc3f7"
    property color surfaceColor: "#1c1c1c"
    property color borderColor: "#333333"
    property color textColor: "#e0e0e0"
    property color dangerColor: "#d32f2f"
    readonly property bool isHighlighted: down || active

    hoverEnabled: true
    padding: 6
    leftPadding: 10
    rightPadding: 10
    topPadding: 4
    bottomPadding: 4

    implicitWidth: Math.max(80, (contentItem ? contentItem.implicitWidth : 0) + leftPadding + rightPadding)
    implicitHeight: Math.max(32, (contentItem ? contentItem.implicitHeight : 0) + topPadding + bottomPadding)
    opacity: enabled ? 1 : 0.4

    background: Rectangle {
        radius: 4
        anchors.fill: parent
        color: control.isHighlighted
               ? (control.danger ? control.dangerColor : control.accentColor)
               : control.surfaceColor
        border.color: control.isHighlighted
                      ? (control.danger ? control.dangerColor : control.accentColor)
                      : control.borderColor
        border.width: 1
    }

    contentItem: Text {
        text: control.text
        color: control.isHighlighted ? "#ffffff" : control.textColor
        font.pixelSize: 13
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
        width: control.availableWidth
        height: control.availableHeight
    }
}
