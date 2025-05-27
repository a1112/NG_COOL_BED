import QtQuick
import "../core"
Rectangle {

    //property rect rect_box: value
    property ObjectType objectType: ObjectType{}
    color: "#22000000"
    border.width: 2
    border.color: "green"
    x:objectType.rect_.x
    y:objectType.rect_.y
    width:objectType.rect_.width
    height:objectType.rect_.height

}
