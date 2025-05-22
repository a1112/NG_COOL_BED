import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
  // 自动
CheckDelegate {
    height: parent.height
    implicitHeight: parent.height
    text: qsTr("AUTO ") + (!cool_bed_core.auto_check? cool_bed_core.to_auto_true_count:"")
    checked: cool_bed_core.auto_check
    onCheckedChanged:  cool_bed_core.auto_check = checked
}
