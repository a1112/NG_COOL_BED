import QtQuick
import QtQuick.Layouts
import "head"
import "view"
import "../types"
import "core"
import "data"
// 单个冷床视图


ColumnLayout {
    Layout.fillWidth: true
    Layout.fillHeight: true
    property CoolBedModelType cool_bed_model_type:CoolBedModelType{}
    property CoolBedCore cool_bed_core: CoolBedCore{}

    Head{
    }

    ImageView{

    }
    DataView{

    }
}
