import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../core" as Core
import "."
import "camera_panel"
import "mapping_panel"
SplitView {
    id: root
    spacing: 8
    orientation: Qt.Vertical


    Frame {
        id: cameraFrame
        SplitView.fillWidth: true
        SplitView.fillHeight: true

        padding: 8
        background: Rectangle { color: "#101010"; radius: 4 }
        CameraPanel {
            id: cameraPanelRoot
            anchors.fill: parent
        }
    }
    MappingPanel{
        id: mappingPanelRoot
    }

}
