import QtQuick
import QtQuick.Controls.Material
TabBar {
    id:root
    currentIndex: cool_bed_core.current_index
    onCurrentIndexChanged: cool_bed_core.current_index = currentIndex
    Repeater{
        model: cool_bed_model_type.groupModel
        delegate: GroupButton{
            height: root.height
            implicitHeight: height
        }
    }
}
