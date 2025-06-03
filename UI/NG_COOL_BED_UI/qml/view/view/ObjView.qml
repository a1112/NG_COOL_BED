import QtQuick

Item {
    id: root
    Repeater{
        model: cool_bed_core.coolBedDataType.current_item.objcetList
        delegate : ObjectItem{
        }
    }

}
