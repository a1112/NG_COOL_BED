import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

import QtWebSockets

ApplicationWindow {
    id: root

    width: 860
    height: 620
    title: qsTr("算法测试")


    property var modelList: []
    property string selectedModel: ""
    property string targetFolder: ""
    property string outputFolder: ""
    property real threshold: 0.40
    property string mode: "copy"
    property bool optionClassify: true
    property bool optionSaveLabel: false
    property bool optionPriority: false
    property bool running: false
    property bool loadingModels: false
    property int processedCount: 0
    property int totalCount: 0
    property real progressSpeed: 0
    property real etaSeconds: 0
    property string statusMessage: ""
    property string currentTaskId: ""

    signal startRequested()

    function openDialog() {
        if (!visible)
            visible=true
        if (!modelList.length)
            refreshModels()
    }

    onVisibleChanged: {
        if (!visible) {
            running = false
            progressSocket.active = false
        }
    }

    function refreshModels() {
        if (!app_api || !app_api.get_alg_models) {
            statusMessage = qsTr("缺少模型列表接口")
            return
        }
        loadingModels = true
        statusMessage = qsTr("请求模型列表...")
        app_api.get_alg_models(
                    function(text) {
                        loadingModels = false
                        var parsed = []
                        try {
                            var js = JSON.parse(text)
                            if (js && js.models)
                                parsed = js.models
                            else if (Array.isArray(js))
                                parsed = js
                        } catch(e) {
                            console.warn("get_alg_models parse error", e)
                        }
                        if (!parsed || !parsed.length)
                            parsed = []
                        modelList = parsed
                        if (parsed.length) {
                            if (parsed.indexOf(selectedModel) === -1)
                                selectedModel = parsed[0]
                            statusMessage = qsTr("模型数量: %1").arg(parsed.length)
                        } else {
                            selectedModel = ""
                            statusMessage = qsTr("未获取到模型")
                        }
                    },
                    function(err) {
                        loadingModels = false
                        statusMessage = qsTr("模型列表获取失败")
                        console.warn("get_alg_models error", err)
                    })
    }

    function cleanUrl(url) {
        if (!url)
            return ""
        var str = url.toString ? url.toString() : url
        return decodeURIComponent(str.replace("file:///", "").replace("file://", ""))
    }

    function validateInputs() {
        if (!selectedModel) {
            statusMessage = qsTr("请选择模型")
            return false
        }
        if (!targetFolder) {
            statusMessage = qsTr("请选择目标文件夹")
            return false
        }
        if (!outputFolder) {
            statusMessage = qsTr("请选择输出文件夹")
            return false
        }
        return true
    }

    function progressUrl() {
        if (!app_api || !app_api.server_url)
            return ""
        return app_api.server_url.wsServerUrl + "/alg/test/progress"
    }

    function startTest() {
        if (running)
            return
        if (!validateInputs())
            return
        if (!app_api || !app_api.start_alg_test) {
            statusMessage = qsTr("缺少启动接口")
            return
        }
        running = true
        processedCount = 0
        totalCount = 0
        progressSpeed = 0
        etaSeconds = 0
        currentTaskId = ""
        statusMessage = qsTr("正在启动算法测试...")
        logModel.clear()
        appendLog(qsTr("开始执行: %1").arg(selectedModel))
        openProgressSocket()
        const payload = {
            model: selectedModel,
            target: targetFolder,
            output: outputFolder,
            threshold: threshold,
            mode: mode,
            options: {
                classify_save: optionClassify,
                save_label: optionSaveLabel,
                prioritize: optionPriority
            }
        }
        app_api.start_alg_test(
                    payload,
                    function(text) {
                        var js = {}
                        try { js = JSON.parse(text) } catch(e) { js = {} }
                        if (js && js.task_id)
                            currentTaskId = js.task_id
                        if (js && js.message)
                            appendLog(js.message)
                        statusMessage = qsTr("任务已启动")
                    },
                    function(err) {
                        running = false
                        progressSocket.active = false
                        statusMessage = qsTr("启动失败")
                        appendLog(qsTr("启动失败: %1").arg(err))
                    })
    }

    function stopTest() {
        if (!running) {
            progressSocket.active = false
            return
        }
        running = false
        progressSocket.active = false
        statusMessage = qsTr("已请求停止")
        if (app_api && app_api.stop_alg_test) {
            app_api.stop_alg_test(
                        { task_id: currentTaskId },
                        function(){ appendLog(qsTr("服务端已确认停止")) },
                        function(err){ appendLog(qsTr("停止接口失败: %1").arg(err)) })
        }
    }

    function openProgressSocket() {
        const url = progressUrl()
        if (!url) {
            appendLog(qsTr("WebSocket 地址无效"))
            return
        }
        progressSocket.active = false
        progressSocket.url = url
        progressSocket.active = true
    }

    function appendLog(msg) {
        const stamp = Qt.formatDateTime(new Date(), "hh:mm:ss")
        logModel.append({ text: stamp + "  " + msg })
        const maxRows = 200
        if (logModel.count > maxRows)
            logModel.remove(0, logModel.count - maxRows)
    }

    function formatEta(seconds) {
        if (!seconds || seconds <= 0 || seconds === Infinity)
            return qsTr("计算中")
        const mins = Math.floor(seconds / 60)
        const secs = Math.floor(seconds % 60)
        if (mins > 60) {
            const hours = Math.floor(mins / 60)
            const leftMin = mins % 60
            return qsTr("%1小时%2分").arg(hours).arg(leftMin)
        }
        if (mins > 0)
            return qsTr("%1分%2秒").arg(mins).arg(secs)
        return qsTr("%1秒").arg(secs)
    }

    ListModel { id: logModel }

    FileDialog {
        id: targetFolderDialog
        title: qsTr("选择目标文件夹")
        fileMode: FileDialog.OpenDirectory
        onAccepted: {
            if (selectedFiles && selectedFiles.length > 0)
                targetFolder = cleanUrl(selectedFiles[0])
        }
    }

    FileDialog {
        id: outputFolderDialog
        title: qsTr("选择输出文件夹")
        fileMode: FileDialog.OpenDirectory
        onAccepted: {
            if (selectedFiles && selectedFiles.length > 0)
                outputFolder = cleanUrl(selectedFiles[0])
        }
    }

    WebSocket {
        id: progressSocket
        active: false
        url: ""
        onStatusChanged: {
            if (status === WebSocket.Error) {
                appendLog(qsTr("进度连接错误: %1").arg(errorString))
                statusMessage = errorString
            } else if (status === WebSocket.Closed && running) {
                appendLog(qsTr("进度连接已关闭"))
            }
        }
        onTextMessageReceived: function(message) {
            var js = {}
            try { js = JSON.parse(message) } catch(e) { js = { message: message } }
            if (js.task_id && !currentTaskId)
                currentTaskId = js.task_id
            if (js.speed !== undefined)
                progressSpeed = js.speed
            if (js.done !== undefined)
                processedCount = js.done
            if (js.total !== undefined)
                totalCount = js.total
            if (js.eta !== undefined)
                etaSeconds = js.eta
            if (js.message)
                appendLog(js.message)
            if (js.status)
                statusMessage = js.status
            if (js.finished || js.state === "finished") {
                running = false
                appendLog(js.summary ? js.summary : qsTr("任务完成"))
                progressSocket.active = false
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10

        GridLayout {
            Layout.fillWidth: true
            columns: 3
            columnSpacing: 12
            rowSpacing: 10

            Label { text: qsTr("模型"); Layout.alignment: Qt.AlignVCenter }
            ComboBox {
                id: modelCombo
                Layout.fillWidth: true
                model: modelList
                enabled: !loadingModels
                textRole: ""
                displayText: selectedModel || qsTr("请选择模型")
                onActivated: function(index) {
                    if (index >= 0 && index < modelList.length)
                        selectedModel = modelList[index]
                }
                delegate: ItemDelegate {
                    required property int index
                    required property var modelData
                    width: modelCombo.width
                    text: modelData
                    onClicked: {
                        modelCombo.currentIndex = index
                        selectedModel = modelData
                        modelCombo.popup.close()
                    }
                }
            }
            RowLayout {
                Button {
                    text: qsTr("刷新")
                    onClicked: refreshModels()
                }
                BusyIndicator {
                    running: loadingModels
                    visible: running
                    width: 20
                    height: 20
                }
            }

            Label { text: qsTr("目标文件夹"); Layout.alignment: Qt.AlignVCenter }
            TextField {
                Layout.fillWidth: true
                text: targetFolder
                placeholderText: qsTr("请选择需要测试的图像根目录")
                onEditingFinished: targetFolder = text.trim()
            }
            Button {
                text: qsTr("选择")
                onClicked: targetFolderDialog.open()
            }

            Label { text: qsTr("输出文件夹"); Layout.alignment: Qt.AlignVCenter }
            TextField {
                Layout.fillWidth: true
                text: outputFolder
                placeholderText: qsTr("保存结果的目录")
                onEditingFinished: outputFolder = text.trim()
            }
            Button {
                text: qsTr("选择")
                onClicked: outputFolderDialog.open()
            }

            Label { text: qsTr("低置信度阈值"); Layout.alignment: Qt.AlignVCenter }
            RowLayout {
                Layout.fillWidth: true
                Slider {
                    id: thresholdSlider
                    Layout.fillWidth: true
                    from: 0
                    to: 100
                    value: threshold * 100
                    stepSize: 1
                    onValueChanged: threshold = value / 100
                }
                TextField {
                    width: 60
                    inputMethodHints: Qt.ImhFormattedNumbersOnly
                    text: threshold.toFixed(2)
                    onEditingFinished: {
                        var val = parseFloat(text)
                        if (isNaN(val))
                            val = 0.4
                        val = Math.max(0, Math.min(1, val))
                        threshold = val
                        text = threshold.toFixed(2)
                        thresholdSlider.value = threshold * 100
                    }
                }
            }
            Item { width: 1; height: 1 }

            Label { text: qsTr("模式"); Layout.alignment: Qt.AlignVCenter }
            RowLayout {
                Layout.fillWidth: true
                ButtonGroup { id: modeGroup }
                RadioButton {
                    text: qsTr("复制")
                    checked: mode === "copy"
                    onClicked: mode = "copy"
                    ButtonGroup.group: modeGroup
                }
                RadioButton {
                    text: qsTr("移动")
                    checked: mode === "move"
                    onClicked: mode = "move"
                    ButtonGroup.group: modeGroup
                }
            }
            Item { width: 1; height: 1 }
        }

        Frame {
            Layout.fillWidth: true
            background: Rectangle { color: "#111"; radius: 4 }
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 24
                Label {
                    text: qsTr("多选")
                    color: "#9e9e9e"
                }
                CheckBox {
                    text: qsTr("分类保存")
                    checked: optionClassify
                    onToggled: optionClassify = checked
                }
                CheckBox {
                    text: qsTr("保存标注文件")
                    checked: optionSaveLabel
                    onToggled: optionSaveLabel = checked
                }
                CheckBox {
                    text: qsTr("测试优先")
                    checked: optionPriority
                    onToggled: optionPriority = checked
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Button {
                text: running ? qsTr("执行中...") : qsTr("开始测试")
                enabled: !running
                onClicked: startTest()
            }
            Button {
                text: qsTr("停止")
                enabled: running
                onClicked: stopTest()
            }
            Item { Layout.fillWidth: true }
            Label {
                text: statusMessage
                color: "#90caf9"
                elide: Text.ElideRight
                Layout.preferredWidth: 380
            }
        }

        ProgressBar {
            Layout.fillWidth: true
            from: 0
            to: Math.max(totalCount, 1)
            value: processedCount
        }

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: qsTr(" %1 / %2 张").arg(processedCount).arg(totalCount || qsTr("未知"))
            }
            Label {
                text: qsTr("速度 %1 张/秒").arg(progressSpeed.toFixed(2))
            }
            Label {
                text: qsTr("预计 %1").arg(formatEta(etaSeconds))
            }
            Item { Layout.fillWidth: true }
        }

        Frame {
            Layout.fillWidth: true
            Layout.fillHeight: true
            background: Rectangle { color: "#080808"; radius: 4 }
            ListView {
                id: logList
                anchors.fill: parent
                clip: true
                model: logModel
                delegate: Text {
                    width: logList.width - 20
                    text: model.text
                    color: "#e0e0e0"
                    wrapMode: Text.WrapAnywhere
                }
            }
        }
    }
}
