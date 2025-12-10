import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

SplitView {
    SplitView.fillWidth: true
    SplitView.preferredHeight: 360
    spacing: 2
    function adjustZoom(delta) {
        perspective.adjustZoom(delta)
    }

    Frame {
        SplitView.fillWidth: true
        SplitView.fillHeight: true
        padding: 8
        background: Rectangle { color: "#111"; radius: 4 }
        PerspectivePreview {
            id: perspective
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
