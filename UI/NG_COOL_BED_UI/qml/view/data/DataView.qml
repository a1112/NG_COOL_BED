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
        DataLabelItem{
            width: 150
            msg:"使用的相机组合"
            key:"KEY"
            value:cool_bed_core.coolBedDataType.current_item.use_group_key
        }
        DataLabelEx{
            width: 150
            msg: "是否存在错误？"
            key: "ERROR?"
            has: cool_bed_core.coolBedDataType.current_item.has_error
        }
    }


    Column{
    Row{
        DataLabelEx{
            width: 80
            msg:"冷床左侧是否有板"
            key:"CL"
            has: cool_bed_core.coolBedDataType.current_item.left_cool_bed_has_steel
        }
        DataLabelEx{
            width: 80
            msg:"冷床右侧是否有板"
            key:"CR"
            has:  cool_bed_core.coolBedDataType.current_item.right_cool_bed_has_steel
        }
    }
    Row{
        DataLabelEx{
            width: 80
            msg:"辊道左侧是否有板"
            key:"RL"
            has:cool_bed_core.coolBedDataType.current_item.left_roll_bed_has_steel
        }
        DataLabelEx{
            width: 80
            msg:"辊道右侧是否有板"
            key:"RR"
            has:cool_bed_core.coolBedDataType.current_item.right_roll_bed_has_steel
        }
    }


    }

    Row{
        DataLabelItem{
            width: 120
            msg:"左侧距离辊道中心距离"
            key:"LC"
            value:parseInt(cool_bed_core.coolBedDataType.current_item.left_under_steel_to_center) /1000
        }
        DataLabelItem{
            width: 120
            msg: "右侧距离辊道中心距离"
            key: "RC"
            value:parseInt( cool_bed_core.coolBedDataType.current_item.right_under_steel_to_center) /1000
        }
    }


    Item{
        Layout.fillHeight: true
        Layout.fillWidth: true
        SteelInfoList{

        }
    }

}
}
