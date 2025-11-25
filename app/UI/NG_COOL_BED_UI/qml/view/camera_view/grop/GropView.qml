import QtQuick
import QtQuick.Layouts
import "."
import "../camera"

ColumnLayout {
    id: root
    property var layoutConfig: null          // {grid: [...]}
    property var cameraForSlot: null         // function(slotNumber) -> camera info
    property int selectedSlot: -1
    property bool offlineMode: false
    property bool showOverlay: true
    property var visibilityMap: ({})
    property var shapesProvider: null

    spacing: 8

    Repeater {
        model: (root.layoutConfig && root.layoutConfig.grid) ? root.layoutConfig.grid.length : 0
        delegate: RowLayout {
            property var rowData: (root.layoutConfig && root.layoutConfig.grid) ? (root.layoutConfig.grid[index] || []) : []
            spacing: 8
            Layout.fillWidth: true

            Repeater {
                model: rowData.length
                delegate: Loader {
                    property var slotValue: rowData[index]
                    Layout.fillWidth: true
                    // Avoid binding to parent.width to prevent recursive layout; let RowLayout distribute space evenly.
                    Layout.preferredWidth: 220
                    Layout.preferredHeight: 240
                    active: slotValue !== null && slotValue !== undefined
                    sourceComponent: cameraTileComponent
                    property var camera: root.cameraForSlot ? root.cameraForSlot(slotValue) : null
                    property int slotNumber: slotValue
                    property bool selected: slotValue === root.selectedSlot
                }
            }
        }
    }

    Component {
        id: cameraTileComponent
        CameraTile {
            camera: camera
            slotNumber: slotNumber
            selected: selected
            offlineMode: root.offlineMode
            showOverlay: root.showOverlay
            visibilityMap: root.visibilityMap
            shapesProvider: root.shapesProvider
        }
    }
}
