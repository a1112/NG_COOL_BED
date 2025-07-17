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
        spacing: 20
        Column{
            DataLabelItem{
                width: 150
                msg:"使用的相机组合"
                key:"使用组合"
                value:cool_bed_core.coolBedDataType.current_item.use_group_key
            }
            DataLabelEx{
                width: 150
                msg: "是否存在错误？"
                key: "存在错误:"
                has: cool_bed_core.coolBedDataType.current_item.has_error
            }
        }


        Column{
            Row{
                DataLabelEx{
                    width: 150
                    msg:"冷床左侧是否有板"
                    key:"左冷床有板"
                    has: cool_bed_core.coolBedDataType.current_item.left_cool_bed_has_steel
                }
                DataLabelEx{
                    width: 150
                    msg:"右侧是否有板 "
                    key:"右冷床有板"
                    has:  cool_bed_core.coolBedDataType.current_item.right_cool_bed_has_steel
                }
            }


            Row{
                DataLabelItem{
                    width: 150
                    msg:"左侧下料值"
                    key:"左下料"
                    value:parseInt(cool_bed_core.coolBedDataType.current_item.left_cool_bed_steel_to_up)
                    onHoveredChanged: {
                        cool_bed_core.controlConfig.left_move_to_up_hov
                    }

                }

                DataLabelItem{
                    width: 150
                    msg: "右侧下料值"
                    key: "右下料"
                    value:parseInt( cool_bed_core.coolBedDataType.current_item.right_cool_bed_steel_to_up)
                    onHoveredChanged: {
                        cool_bed_core.controlConfig.right_move_to_up_hov
                    }

                }
            }
        }
        Column{
            Row{
                DataLabelEx{
                    width: 150
                    msg:"辊道左侧是否有板"
                    key:"左辊道有板"
                    has:cool_bed_core.coolBedDataType.current_item.left_roll_bed_has_steel
                }
                DataLabelEx{
                    width: 150
                    msg:"辊道右侧是否有板"
                    key:"右辊道有板"
                    has:cool_bed_core.coolBedDataType.current_item.right_roll_bed_has_steel
                }
            }
            Row{
                DataLabelItem{
                    width: 150
                    msg:"左侧居中距离"
                    key:"左居中"
                    value:parseInt(cool_bed_core.coolBedDataType.current_item.left_rool_to_center)
                    onHoveredChanged: {
                        cool_bed_core.controlConfig.left_move_to_up_hov
                    }

                }
                DataLabelItem{
                    width: 150
                    msg: "右侧居中距离"
                    key: "右居中"
                    value:parseInt( cool_bed_core.coolBedDataType.current_item.right_rool_to_center)
                    onHoveredChanged: {
                        cool_bed_core.controlConfig.right_move_to_up_hov
                    }

                }
            }


        }

        Row{
            DataLabelItem{
                width: 150
                msg:"左侧距离辊道中心距离"
                key:"LC"
                value:parseInt(cool_bed_core.coolBedDataType.current_item.left_under_steel_to_center) /1000
            }

            DataLabelItem{
                width: 150
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
