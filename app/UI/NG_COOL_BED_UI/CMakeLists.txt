cmake_minimum_required(VERSION 3.16)

project(NG_COOL_BED_UI VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(RCSOURCES ${RCSOURCES} resources.rc)

find_package(Qt6 REQUIRED COMPONENTS Quick Multimedia)

qt_standard_project_setup(REQUIRES 6.8)

# if(WIN32)

# endif()

qt_add_executable(appNG_COOL_BED_UI
    main.cpp
    ${RCSOURCES}
)

# Embed all QML via qml.qrc (keeps imports working with the qrc:/ scheme)

qt6_add_resources(QML_BUNDLE
    qml.qrc
    resource.qrc
)

target_sources(appNG_COOL_BED_UI PRIVATE ${QML_BUNDLE})


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
