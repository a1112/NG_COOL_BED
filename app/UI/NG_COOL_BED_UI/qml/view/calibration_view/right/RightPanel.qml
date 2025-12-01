import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
import "."

SplitView {
    id: root
    spacing: 8
    orientation: Qt.Vertical


    Frame {
        SplitView.fillWidth: true
        SplitView.fillHeight: true

        padding: 8
        background: Rectangle { color: "#101010"; radius: 4 }
        CameraPanel {
            anchors.fill: parent
        }
    }

    SplitView {
        SplitView.fillWidth: true
        SplitView.preferredHeight: 360
        spacing: 2
        Frame {
            SplitView.fillWidth: true
            SplitView.fillHeight: true
            padding: 8
            background: Rectangle { color: "#111"; radius: 4 }
            PerspectivePreview {
                anchors.fill: parent
            }
        }

        Frame {
            SplitView.preferredWidth: 340
            SplitView.fillHeight: true
            padding: 8
            background: Rectangle { color: "#131313"; radius: 4 }
            MappingObjectPanel {
                anchors.fill: parent
            }
        }
    }

}
