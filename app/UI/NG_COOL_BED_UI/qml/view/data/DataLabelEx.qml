import QtQuick

DataLabelItem {
    property bool has : false
    value: has?"是" : "否"
    value_color: has?"green":"yellow"
}
