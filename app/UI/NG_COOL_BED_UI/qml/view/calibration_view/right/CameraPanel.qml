import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
import "."

ColumnLayout {
    id: root
    spacing: 8
    property real zoomFactor: 1.0
    property real minZoom: 0.4
    property real maxZoom: 4.0
    readonly property real baseWidth: Core.CalibrationViewCore.labelImageWidth || 1
    readonly property real baseHeight: Core.CalibrationViewCore.labelImageHeight || 1
    onZoomFactorChanged: cip.requestRepaint()
    CameraToolbar {
        Layout.fillWidth: true
    }

    SplitView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 8

        CameraImagePanel {
            id:cip
            SplitView.fillWidth: true
            SplitView.fillHeight: true
        }

        ObjectManagerPanel {
            SplitView.preferredWidth: 320
            SplitView.fillHeight: true
        }
    }
}
