import QtQuick
import QtQuick.Layouts
import "../core"
Item {
    Layout.fillWidth: true
    Layout.fillHeight: true

    property MapConfigItem map_config_item: MapConfigItem{
        draw_width:map_view.width
        draw_height: map_view.height

    }


    Image{
        id:old_image
        width: parent.width
        height: parent.height
        fillMode: Image.PreserveAspectFit
        cache: false
    }

    Image{
        id:show_image
        cache: false
        width: parent.width
        height: parent.height
        source: cool_bed_core.source_url
        fillMode: Image.PreserveAspectFit
        onStatusChanged: {
            if (status==Image.Ready){
                old_image.source=source
                t.start()
            }
        }
    }

    Timer{
        id: t
        interval: 300
        running: false
        repeat: false
        onTriggered: {
       // cool_bed_core.flush_source()
            cool_bed_core.flush_source()
        }
    }

    MapView{
        id:map_view
        anchors.centerIn: parent
        width: show_image.paintedWidth
        height: show_image.paintedHeight
    }

    //cool_bed_core.controlConfig.left_move_to_up_hov

    ObjView{
        visible: cool_bed_core.show_det_view
        anchors.centerIn: parent
        width: show_image.paintedWidth
        height: show_image.paintedHeight
    }
    MoveView{
        id:move_view
        anchors.centerIn: parent
        width: show_image.paintedWidth
        height: show_image.paintedHeight

    }
}
