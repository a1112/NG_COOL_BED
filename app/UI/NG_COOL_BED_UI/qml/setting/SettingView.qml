import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: settingRoot
    modal: true
    focus: true
    width: parent ? parent.width * 0.7 : 900
    height: parent ? parent.height * 0.7 : 600
    anchors.centerIn: parent
    property bool busy: false

    function toggleShield(coolBed, groupKey, shield) {
        if (!app_api || !app_api.set_group_shield) {
            console.warn("set_group_shield api missing")
            return
        }
        busy = true
        app_api.set_group_shield({
                                     "cool_bed": coolBed,
                                     "group": groupKey,
                                     "shield": shield
                                 },
                                 function() {
                                     busy = false
                                     app_core.flush()
                                 },
                                 function(err) {
                                     busy = false
                                     console.warn("set_group_shield error", err)
                                 })
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Label {
                text: qsTr("组合优先级与屏蔽设置")
                font.bold: true
                font.pointSize: 16
            }
            Item { Layout.fillWidth: true }
            Button {
                text: qsTr("刷新")
                onClicked: app_core.flush()
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            Column {
                width: parent.width
                spacing: 16

                Repeater {
                    model: app_core.coolBedListModel
                    delegate: Column {
                        width: parent.width
                        spacing: 6
                        property var bedInfo: (function(v) {
                            try { return JSON.parse(v) } catch(e) { return {} }
                        })(data_)
                        property var groupKeys: bedInfo && bedInfo.all ? bedInfo.all : []
                        Label {
                            text: qsTr("冷床：") + cool_bed_key_
                            font.pointSize: 14
                            font.bold: true
                        }
                        Rectangle {
                            width: parent.width
                            height: 1
                            color: "#303030"
                        }
                        Repeater {
                            model: groupKeys.length
                            delegate: RowLayout {
                                Layout.fillWidth: true
                                spacing: 12
                                property string groupKey: groupKeys[index]
                                property var groupInfo: (bedInfo && bedInfo.data && bedInfo.data[groupKey]) ? bedInfo.data[groupKey] : {}
                                CheckBox {
                                    Layout.preferredWidth: 200
                                    text: groupKey + (groupInfo && groupInfo.msg ? (" - " + groupInfo.msg) : "")
                                    checked: !!(groupInfo && groupInfo.shield)
                                    onClicked: settingRoot.toggleShield(cool_bed_key_, groupKey, checked)
                                }
                                Label {
                                    Layout.fillWidth: true
                                    text: qsTr("默认优先级: ") + (groupInfo && groupInfo.priority !== undefined ? groupInfo.priority : "--")
                                }
                            }
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Item { Layout.fillWidth: true }
            BusyIndicator {
                running: settingRoot.busy
                visible: running
                Layout.preferredWidth: 24
                Layout.preferredHeight: 24
            }
            Button {
                text: qsTr("关闭")
                onClicked: settingRoot.close()
            }
        }
    }
}
