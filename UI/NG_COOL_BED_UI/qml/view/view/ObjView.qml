import QtQuick

Item {
    id: root
    Repeater{
        model: cool_bed_core.coolBedDataType.objcetList
        delegate : ObjectItem{
        }
    }

}
