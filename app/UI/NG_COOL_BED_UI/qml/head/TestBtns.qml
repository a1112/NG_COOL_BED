import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
import "../base"

// 数据测试
Row {
    spacing: 8

    ActionButton{
        text: qsTr("保存-切片")
        onClicked: {
            app_api.save_cap()
        }
    }

    ActionButton{
        text: qsTr("上一张")
        onClicked: {
            app_api.test_pre_image()
        }
    }

    ActionButton{
        text: qsTr("下一张")
        onClicked: {
            app_api.test_next_image()
        }
    }
}
