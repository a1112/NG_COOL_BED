import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core
import "."

ColumnLayout {
    id: root
    spacing: 8

    CameraToolbar {
        Layout.fillWidth: true
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 8

        CameraImagePanel {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }

        ObjectManagerPanel {
            Layout.preferredWidth: 320
            Layout.fillHeight: true
        }
    }
}
