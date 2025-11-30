pragma Singleton
import QtQuick
import "../api" as ApiMod

Item {
    id: core

    // 透视层相关 & 视图状态
    property bool offlineMode: true//(typeof app_core !== "undefined" && app_core) ? app_core.debug : false
    property bool showOverlay: true
    property var overlayVisibility: ({})
    property var overlayLabels: []

    // 视图切换 / 布局
    property int selectedLayoutType: 0      // 0: 组合视图, 1: 单相机
    property int selectedLayoutIndex: 0
    property int selectedSlotNumber: -1
    // QML ListElement 不支持 JS 数组字面量，改用 JS 数组存储
    property var layoutConfigs: [
        { "key": "all", "name": "全部相机 (4x4)", "grid": [[1, null, null, 6],[2,3,4,5],[7,13,null,12],[8,9,10,11]] },
        { "key": "L1",  "name": "一号冷床 (2x4)", "grid": [[1, null, null, 6],[2,3,4,5]] },
        { "key": "L2",  "name": "二号冷床 (2x4)", "grid": [[7,13,null,12],[8,9,10,11]] }
    ]

    // 数据状态
    property string calibrateKey: ""
    property var cameraManageData: ({})
    property var cameraOverlayMap: ({})
    property var labelmeCache: ({})
    property var cameraInfo: []
    property var cameraBySeq: ({})
    property var flatTreeRows: []

    property string statusMessage: ""

    function currentLayoutConfig() {
        const count = layoutConfigs ? layoutConfigs.length : 0
        if (!count) return null
        const idx = Math.min(Math.max(selectedLayoutIndex, 0), count - 1)
        return layoutConfigs[idx]
    }

    function layoutIndexForSlot(slotNumber) {
        if (slotNumber === null || slotNumber === undefined) return -1
        const count = layoutConfigs ? layoutConfigs.length : 0
        for (var i = count - 1; i >= 0; --i) {
            const cfg = layoutConfigs[i]
            const grid = cfg && cfg.grid ? cfg.grid : []
            for (var r = 0; r < grid.length; ++r) {
                const row = grid[r] || []
                if (row.indexOf(slotNumber) !== -1) return i
            }
        }
        return -1
    }

    function currentCamera() {
        return cameraForSlot ? cameraForSlot(selectedSlotNumber) : null
    }

    function loadJson(path) {
        const xhr = new XMLHttpRequest()
        xhr.open("GET", path, false)
        xhr.send()
        if (xhr.status === 200 || xhr.status === 0) {
            try { return JSON.parse(xhr.responseText) } catch(e) { console.warn("JSON parse failed", path, e) }
        } else {
            console.warn("loadJson failed", path, xhr.status)
        }
        return null
    }

    function loadCurrentCalibrate() {
        // 通过后端 API 获取 current，失败则返回默认
        try {
            if (ApiMod.Api && ApiMod.Api.server_url) {
                const url = ApiMod.Api.server_url.url(ApiMod.Api.server_url.serverUrl, "config", "calibrate")
                const remoteCfg = loadJson(url)
                if (remoteCfg && remoteCfg.current) return remoteCfg.current
            }
        } catch(e) {
            console.warn("loadCurrentCalibrate remote failed", e)
        }
        return "calibrate"
    }

    function normalizeCameraList(list_) {
        const res = []
        list_.forEach((item) => {
            if (typeof item === "string") res.push({camera: item, shape: "Area"})
            else if (item && item.camera) res.push({camera: item.camera, shape: item.shape || "Area"})
        })
        return res
    }

    function rebuildOverlayMap() {
        const map = {}
        const shapeNames = []
        const groups = (cameraManageData && cameraManageData.group) ? cameraManageData.group : {}
        Object.keys(groups).forEach((lineKey) => {
            const line = groups[lineKey] || {}
            const gList = line.group || []
            gList.forEach((g) => {
                const camList = normalizeCameraList(g.camera_list || [])
                camList.forEach((item) => {
                    const camId = item.camera
                    const shape = (item.shape || "Area")
                    if (!map[camId]) map[camId] = []
                    if (map[camId].indexOf(shape) === -1) map[camId].push(shape)
                    if (shapeNames.indexOf(shape) === -1) shapeNames.push(shape)
                })
            })
        })
        cameraOverlayMap = map
        const vis = {}
        shapeNames.forEach((s) => { vis[s.toLowerCase()] = true })
        overlayVisibility = vis
        overlayLabels = shapeNames
    }

    function deriveSeq(camId) {
        const m = /L(\d+)_([0-9]+)/i.exec(camId)
        if (m) {
            const line = parseInt(m[1])
            const idx = parseInt(m[2])
            if (!isNaN(line) && !isNaN(idx)) {
                const offset = (line - 1) * 6
                return offset + idx
            }
        }
        return camId
    }

    function getLabelme(camId) {
        if (labelmeCache[camId]) return labelmeCache[camId]
        if (!(ApiMod.Api && ApiMod.Api.server_url)) {
            console.warn("server_url missing, skip label load for", camId)
            return null
        }
        const url = ApiMod.Api.server_url.url(ApiMod.Api.server_url.serverUrl, "calibrate", "label", calibrateKey, camId)
        const data = loadJson(url)
        if (data) labelmeCache[camId] = data
        return data
    }

    function snapshotPath(camId) {
        const lm = getLabelme(camId)
        const imgName = lm && lm.imagePath ? lm.imagePath : camId + ".jpg"
        if (ApiMod.Api && ApiMod.Api.server_url) {
            return ApiMod.Api.server_url.url(ApiMod.Api.server_url.serverUrl, "calibrate", "image", calibrateKey, imgName)
        }
        console.warn("server_url missing, snapshot fallback empty")
        return ""
    }

    function shapesForCamera(camId) {
        if (!camId || !showOverlay) return []
        const lm = getLabelme(camId)
        if (!lm || !lm.shapes) return []
        const wanted = cameraOverlayMap[camId] || []
        const res = []
        lm.shapes.forEach((shapeObj) => {
            const label = shapeObj.label || ""
            const key = label.toLowerCase()
            const allowedByCamera = wanted.length === 0 || wanted.some((s) => s.toLowerCase() === key)
            if (allowedByCamera) {
                res.push({
                    label: label,
                    points: shapeObj.points || [],
                    imageWidth: lm.imageWidth || 1,
                    imageHeight: lm.imageHeight || 1
                })
            }
        })
        return res
    }

    function buildCameraInfo(remoteList) {
        const remoteById = {}
        if (remoteList && remoteList.length) {
            remoteList.forEach((item) => { if (item && item.camera) remoteById[item.camera] = item })
        }

        const entries = []
        const bySeq = {}
        const rows = []
        if (remoteList && remoteList.length) {
            const bedSet = {}
            remoteList.forEach((item) => {
                const camId = item.camera
                const bed = item.bed || ""
                const seq = item.seq || deriveSeq(camId)
                const entry = {
                    id: camId,
                    label: camId,
                    bed: bed,
                    seq: seq,
                    ip: item.ip || "",
                    rtsp_url: item.rtsp_url || "",
                    position: item.position || "",
                    enabled: item.enable !== false,
                    snapshot: snapshotPath(camId)
                }
                entries.push(entry)
                if (seq !== undefined && seq !== null) bySeq[seq] = entry
                if (!bedSet[bed]) {
                    bedSet[bed] = true
                    rows.push({level: 0, display: bed || "未知分组", ip: "", seq: "", position: ""})
                }
                rows.push({
                    level: 1,
                    display: camId,
                    ip: entry.ip,
                    seq: seq,
                    position: entry.position || ""
                })
            })
        }

        cameraInfo = entries
        cameraBySeq = bySeq
        flatTreeRows = rows
    }

    function refreshSnapshots() {
        if (!cameraInfo || !cameraInfo.length) return
        const updated = []
        const bySeq = {}
        cameraInfo.forEach((entry) => {
            const camId = entry.id || entry.label || ""
            const clone = Object.assign({}, entry)
            clone.snapshot = camId ? snapshotPath(camId) : ""
            updated.push(clone)
            if (clone.seq !== undefined && clone.seq !== null) bySeq[clone.seq] = clone
        })
        cameraInfo = updated
        cameraBySeq = bySeq
    }

    function reloadFromServer() {
        calibrateKey = loadCurrentCalibrate()
        labelmeCache = ({})
        cameraManageData = ({})
        if (ApiMod.Api && ApiMod.Api.server_url) {
            const url = ApiMod.Api.server_url.url(ApiMod.Api.server_url.serverUrl, "calibrate", "camera_manage", calibrateKey)
            const data = loadJson(url)
            if (data) cameraManageData = data
        }
        rebuildOverlayMap()
        refreshSnapshots()
        statusMessage = "已从后端加载配置"
    }

    function refreshFromApi() {
        if (!ApiMod.Api || !ApiMod.Api.get_cameras) {
            buildCameraInfo([])
            statusMessage = "缺少 API，无法获取相机列表"
            return
        }
        statusMessage = "请求相机信息..."
        ApiMod.Api.get_cameras(
            (text)=>{
                try{
                    const data = JSON.parse(text)
                    buildCameraInfo(data)
                    statusMessage = "相机信息已刷新"
                }catch(e){
                    statusMessage = "相机信息解析失败"
                    buildCameraInfo([])
                }
            },
            (err)=>{
                console.warn("get_cameras error", err)
                statusMessage = "接口错误"
                buildCameraInfo([])
            })
    }

    function cameraForSlot(slotNumber) {
        return cameraBySeq[slotNumber]
    }

    function setOverlayVisibility(label, visible) {
        var vis = {}
        for (var k in overlayVisibility) vis[k] = overlayVisibility[k]
        vis[label.toLowerCase()] = visible
        overlayVisibility = vis
    }

    Component.onCompleted: {
        reloadFromServer()
        refreshFromApi()
    }
}
