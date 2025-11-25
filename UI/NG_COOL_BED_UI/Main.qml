import "qml"
import "qml/api"
import "qml/core"
import "qml/dialogs"
import "qml/menus"
import "qml/setting"
import QtQuick.Controls.Material
MainLayout {    //主界面
    Material.theme: Material.Dark
    property Core app_core: Core{}  // core
    property Api app_api: Api{}     // api
    property Tool app_tool: Tool{}  // 工具
    property Config app_config : Config{}  // config
    // DIALOGES
    property SendDialog send_dialog: SendDialog{}
    property MapDialog map_dialog: MapDialog{}
    property ToolMenus tool_menu: ToolMenus{}
    property SettingView settingView: SettingView{}
}
