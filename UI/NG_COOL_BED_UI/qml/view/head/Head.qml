import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../base"

HeadBase {
    id:root
    Layout.fillWidth: true

    height: 30
    RowLayout{
        anchors.fill: parent
        spacing: 10
        Item{
            width: 20
        }
        AutoCheckDelegate{
        }

        GroupButtonListView{
            height: root.height
        }

        Item{
            Layout.fillWidth: true
        }

        Label {
            Material.foreground: Material.Green
            font.pointSize: 15
            text: cool_bed_model_type.cool_bed_key+"  "
        }
        Label {

            font.pointSize: 10
            text:cool_bed_core.current_key
        }
        Item{
            Layout.fillWidth: true
        }

        ComboBox{
             height: root.height+5
             scale: 0.7
               implicitHeight: root.height+5
            model: ["透视-视图 ","模拟-视图 "]
        }

        CheckDelegate{
            implicitHeight: root.height
            text: qsTr("背景标注")
            checked: cool_bed_core.show_map_view
            onCheckedChanged: cool_bed_core.show_map_view = checked
        }
        CheckDelegate{
            implicitHeight: root.height
            text: qsTr("检测标注")
            checked: cool_bed_core.show_det_view
            onCheckedChanged: cool_bed_core.show_det_view = checked
        }
        Item{
            width: 50
        }
        Label {
            text: cool_bed_core.cap_index
        }
        Item{
            width: 20
        }
    }
}
