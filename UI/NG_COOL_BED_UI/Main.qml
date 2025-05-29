import "qml"
import "qml/api"
import "qml/core"
import "qml/dialogs"
MainLayout {
    property Core app_core: Core{}
    property Api app_api: Api{}
    property Tool app_tool: Tool{}

    property Config app_config:Config{}

    property SendDialog send_dialog: SendDialog{

    }
}
