import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

// 数据显示

Item {
    Layout.fillWidth: true
    height : 50
    id:root
    Pane{
        anchors.fill: parent
        // color: "#00000000"
        // border.color: "blue"
        // border.width: 1

    }
RowLayout{
    anchors.fill: parent
    Column{
    Row{
        DataLabelEx{
            msg:"冷床左侧是否有板"
            key:"CL"
            value: cool_bed_core.coolBedDataType.left_cool_bed_has_steel
        }
        DataLabelEx{
            msg:"冷床右侧是否有板"
            key:"CR"
            value: "是"
        }
    }
    Row{
        DataLabelEx{
            msg:"辊道左侧是否有板"
            key:"RL"
            value: "是"
        }
        DataLabelEx{
            msg:"辊道右侧是否有板"
            key:"RR"
            value: "是"
        }
    }
    }

}
}
