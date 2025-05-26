import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls.Material
import "head"
import "core"
import "view"
import "api"
ApplicationWindow {
    Material.theme: Material.Dark
    width: Screen.width*0.7
    height: Screen.height*0.85
    visible: true
    background: Rectangle{color: "#000" }


    title: app_core.title_text
    ColumnLayout{
        anchors.fill: parent
        HeadView{
        }
        ColumnLayout{
            Layout.fillWidth: true
            Layout.fillHeight: true

            Repeater{
                model: app_core.coolBedListModel
                delegate: CoolBedView{


                }
            }



        }

}
}
