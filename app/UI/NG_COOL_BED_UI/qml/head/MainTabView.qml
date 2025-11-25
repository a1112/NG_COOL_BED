import QtQuick
import QtQuick.Controls
TabBar {
    implicitHeight: 40
    onCurrentIndexChanged: app_core.app_index = currentIndex
    TabButton{
        implicitHeight: 40
        text: qsTr("主要视图")
    }

    TabButton{
        implicitHeight: 40
        text: qsTr("相机视图")
    }

    TabButton{
        implicitHeight: 40
        text: qsTr("标定视图")
    }
}
