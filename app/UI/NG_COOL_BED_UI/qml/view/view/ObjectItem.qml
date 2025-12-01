import QtQuick
import QtQuick.Controls.Material
import "../view_core"
Rectangle {

    // property rect rect_box: value
    property ObjectType objectType: ObjectType{}

    color : "#22000000"
    border.width : 2
    border.color : "green"
    x : objectType.rect_.x
    y : objectType.rect_.y
    width:  objectType.rect_.width
    height : objectType.rect_.height

    Label{
        text : objectType.vis_str
        background : Rectangle{
            color : "#000"
        }
    }

    Label{
        font.pixelSize: 18
        anchors.bottom : parent.bottom
        anchors.right : parent.right
        text : objectType.y_t_c
        background : Rectangle{
            color : "#000"
        }
    }

    Label{
        anchors.centerIn: parent
        font.pixelSize: 18
        font.bold: true
        color: "pink"
        text: objectType.rotated_

    }

    Label{
        font.pixelSize: 18
        anchors.top : parent.top
        anchors.right : parent.right
        text : objectType.name_
        font.bold: true
        color: "green"
    }
    ItemDelegate{
        anchors.fill: parent
        ToolTip.visible: hovered
        ToolTip.text: objectType.info_str
    }
    Column{
        anchors.bottom : parent.bottom
        anchors.left:parent.left
    Row{
        HasRec{
            has: objectType.i_left && objectType.i_cool_bed
        }
        HasRec{
            has: objectType.i_right && objectType.i_cool_bed
        }
    }
    Row{
        HasRec{
            has: objectType.i_left && objectType.i_roll
        }
        HasRec{
            has: objectType.i_right && objectType.i_roll
        }
    }
    }



}
