import QtQuick
import QtQuick.Layouts

Item {
    Layout.fillWidth: true
    Layout.fillHeight: true
    Image{
        id:old_image
        width: parent.width
        height: parent.height
        fillMode: Image.PreserveAspectFit
        cache: false
    }
    Image{
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
        interval: 200
        running: false
        repeat: false
        onTriggered: {
       // cool_bed_core.flush_source()
            cool_bed_core.flush_source()
        }
    }
}
