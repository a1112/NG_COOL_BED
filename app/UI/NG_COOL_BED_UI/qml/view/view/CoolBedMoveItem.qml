import QtQuick
import QtQuick.Controls

Rectangle{
    property int value: 0
    color: "red"
    width: 3
    x:map_config_item.up.x
    y:map_config_item.up.y-height
    height:500

    Label{
    anchors.left: parent.right
    anchors.verticalCenter: parent.verticalCenter
        text: value/1000  +" m"
        color: "red"
        background: Rectangle{
            color: "#000"
        }
    }

}
