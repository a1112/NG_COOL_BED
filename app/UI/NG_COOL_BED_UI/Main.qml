import "qml"
import "qml/api"
import "qml/core"
import "qml/dialogs"
import "qml/menus"
import "qml/setting"
import QtQuick.Controls.Material
MainLayout {    //主界面
    Material.theme: Material.Dark
    property var app_core: Core     // core singleton
    property var app_api: Api       // api singleton
    property Tool app_tool: Tool{}  // 工具
    property Config app_config : Config{}  // config
    // DIALOGES
    property SendDialog send_dialog: SendDialog{}
    property MapDialog map_dialog: MapDialog{}
    property AlgTestDialog alg_test_dialog: AlgTestDialog{}
    property ToolMenus tool_menu: ToolMenus{}
    property SettingView settingView: SettingView{}
}
