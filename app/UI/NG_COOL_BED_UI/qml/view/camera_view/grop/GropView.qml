import QtQuick
import QtQuick.Layouts
import "."
import "../camera"
import "../../../core" as Core

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
                    Layout.preferredWidth: 220
                    Layout.preferredHeight: 240
                    active: slotValue !== null && slotValue !== undefined
                    sourceComponent: cameraTileComponent
                }
            }
        }
    }

    Component {
        id: cameraTileComponent
        CameraTile {
            camera:  root.cameraForSlot ? root.cameraForSlot(slotValue) : null
            slotNumber: slotValue
            selected:  slotValue === root.selectedSlot
            offlineMode: root.offlineMode
            showOverlay: root.showOverlay
            visibilityMap: root.visibilityMap
            shapesProvider: root.shapesProvider
            onTileDoubleClicked: {
                if (slotNumber === null || slotNumber === undefined) return
                Core.CameraViewCore.selectedSlotNumber = slotNumber
                const idx = Core.CameraViewCore.layoutIndexForSlot(slotNumber)
                if (idx >= 0) Core.CameraViewCore.selectedLayoutIndex = idx
                Core.CameraViewCore.selectedLayoutType = 1
            }
        }
    }
}
