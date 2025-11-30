import QtQuick
import QtQuick.Controls.Material
import QtQuick.Layouts
// 数据测试
Row {
    Button{
        text: qsTr("保存-切片")
        onClicked: {
            app_api.save_cap()
        }
    }


    Button{
        text: qsTr("上一张")
        onClicked: {
            app_api.test_pre_image()
        }

    }
    Button{
        text: qsTr("下一张")
        onClicked: {
            app_api.test_next_image()
        }
    }
}
