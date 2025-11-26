import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../core" as Core
import "."

ColumnLayout {
    id: root
    spacing: 8

    RowLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 8

        Frame {
            Layout.fillWidth: true
            Layout.fillHeight: true
            padding: 8
            background: Rectangle { color: "#111"; radius: 4 }
            PerspectivePreview {
                anchors.fill: parent
            }
        }

        Frame {
            Layout.preferredWidth: 340
            Layout.fillHeight: true
            padding: 8
            background: Rectangle { color: "#131313"; radius: 4 }
            MappingObjectPanel {
                anchors.fill: parent
            }
        }
    }

    Frame {
        Layout.fillWidth: true
        Layout.preferredHeight: 360
        padding: 8
        background: Rectangle { color: "#101010"; radius: 4 }
        CameraPanel {
            anchors.fill: parent
        }
    }
}
