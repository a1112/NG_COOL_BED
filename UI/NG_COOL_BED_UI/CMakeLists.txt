cmake_minimum_required(VERSION 3.16)

project(NG_COOL_BED_UI VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Quick)

qt_standard_project_setup(REQUIRES 6.8)

qt_add_executable(appNG_COOL_BED_UI
    main.cpp
)

qt_add_qml_module(appNG_COOL_BED_UI
    URI NG_COOL_BED_UI
    VERSION 1.0
    QML_FILES
        Main.qml
        QML_FILES qml/MainLayout.qml
        QML_FILES qml/head/HeadView.qml
        QML_FILES
        QML_FILES qml/core/Core.qml
        QML_FILES qml/api/Ajax.qml
        QML_FILES qml/api/Api.qml
        QML_FILES qml/api/ServerUrl.qml
        QML_FILES qml/view/CoolBedView.qml
        QML_FILES qml/view/head/Head.qml
        QML_FILES qml/view/view/ImageView.qml
        QML_FILES qml/base/HeadBase.qml
        QML_FILES qml/api/Tool.qml
        QML_FILES qml/types/CoolBedModelType.qml
        QML_FILES qml/view/head/GroupButtonListView.qml
        QML_FILES qml/view/head/GroupButton.qml
        QML_FILES qml/view/head/AutoCheckDelegate.qml
        QML_FILES qml/view/core/CoolBedCore.qml
        QML_FILES qml/view/core/TimeCore.qml
        QML_FILES qml/view/data/DataView.qml
        QML_FILES qml/types/CoolBedDataType.qml
        QML_FILES qml/view/data/DataLabelItem.qml
        QML_FILES qml/view/data/DataLabelEx.qml
        QML_FILES qml/view/core/MapConfig.qml
        QML_FILES qml/view/view/MapView.qml
        QML_FILES qml/view/core/MapConfigItem.qml
        QML_FILES qml/view/view/ObjView.qml
        QML_FILES qml/view/view/ObjectItem.qml
        QML_FILES qml/view/core/ObjectType.qml
        QML_FILES qml/view/data/SteelInfoList.qml
        QML_FILES qml/dialogs/SendDialog.qml
        QML_FILES qml/dialogs/TextViewItem.qml
        QML_FILES qml/api/Config.qml
)

# Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# If you are developing for iOS or macOS you should consider setting an
# explicit, fixed bundle identifier manually though.
set_target_properties(appNG_COOL_BED_UI PROPERTIES
#    MACOSX_BUNDLE_GUI_IDENTIFIER com.example.appNG_COOL_BED_UI
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

target_link_libraries(appNG_COOL_BED_UI
    PRIVATE Qt6::Quick
)

include(GNUInstallDirs)
install(TARGETS appNG_COOL_BED_UI
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
