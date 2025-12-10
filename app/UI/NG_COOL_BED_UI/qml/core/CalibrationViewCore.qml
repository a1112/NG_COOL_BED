pragma Singleton
import QtQuick
import "../api" as ApiMod
import "../core"
Item {
    id: core

    property var folderList: []
    property string currentFolder: ""
    property var cameraManageData: ({})
    property var lineGroupList: []
    property string selectedGroupKey: ""
    property var selectedGroup: ({})

    property var mappingObjects: []
    property var mappingMeta: ({})
    property string perspectiveImageSource: ""
    property real mappingImageWidth: 1
    property real mappingImageHeight: 1
    property var labelShapes: []
    property real labelImageWidth: 1
    property real labelImageHeight: 1
    property string labelImagePath: ""
    property var labelMeta: ({})

    property var cameraRadioList: []
    property string selectedCameraId: ""
    property string cameraImageSource: ""
    property var objectSettings: []

    property bool autoRefresh: false
    property string statusMessage: ""
    property bool busy: false
    property bool offlineMode: Core.debug

    function rebuildFolderList() {
        const cfg = fetchCalibrateConfig()
        const names = (cfg && cfg.available) ? cfg.available.slice() : []
        names.sort()
        folderList = names
        const fromConfig = cfg && cfg.current ? cfg.current : ""
        if ((!currentFolder || names.indexOf(currentFolder) === -1) && names.length) {
            currentFolder = names.indexOf(fromConfig) !== -1 ? fromConfig : names[0]
        } else if (!currentFolder && fromConfig) {
            currentFolder = fromConfig
        }
    }

    function loadCurrentFromConfig() {
        const cfg = fetchCalibrateConfig()
        return cfg && cfg.current ? cfg.current : ""
    }

    onCurrentFolderChanged: {
        if (!currentFolder || currentFolder.length === 0) {
            cameraManageData = ({})
            lineGroupList = []
            selectedGroupKey = ""
            return
        }
        refreshCameraManage()
    }

    onSelectedGroupKeyChanged: applySelectedGroup()

    onSelectedCameraIdChanged: {
        refreshCameraImage()
        loadLabelForCamera(selectedCameraId)
    }

    function refreshFolders() {
        rebuildFolderList()
    }

    function loadJson(path) {
        if (!path) return null
        try {
            const xhr = new XMLHttpRequest()
            xhr.open("GET", path, false)
            xhr.send()
            if (xhr.status === 200 || xhr.status === 0) {
                return JSON.parse(xhr.responseText)
            }
        } catch (e) {
            console.warn("loadJson failed", path, e)
        }
        return null
    }

    function loadText(path) {
        if (!path) return ""
        try {
            const xhr = new XMLHttpRequest()
            xhr.open("GET", path, false)
            xhr.send()
            if (xhr.status === 200 || xhr.status === 0) {
                return xhr.responseText
            }
        } catch (e) {
            console.warn("loadText failed", path, e)
        }
        return ""
    }

    function fetchCalibrateConfig() {
        if (!(ApiMod.Api && ApiMod.Api.server_url)) return {}
        const url = ApiMod.Api.server_url.url(ApiMod.Api.server_url.serverUrl, "config", "calibrate")
        return loadJson(url) || {}
    }

    function cameraManagePath(folder) {
        if (!folder || !(ApiMod.Api && ApiMod.Api.server_url)) return ""
        return ApiMod.Api.server_url.url(ApiMod.Api.server_url.serverUrl, "calibrate", "camera_manage", folder)
    }

    function mappingFilePath(folder, name, ext) {
        if (!folder || !name || !(ApiMod.Api && ApiMod.Api.server_url)) return ""
        return ApiMod.Api.server_url.url(ApiMod.Api.server_url.serverUrl, "calibrate", "mapping", folder, name + "." + ext)
    }

    function labelFilePath(folder, camId) {
        if (!folder || !camId || !(ApiMod.Api && ApiMod.Api.server_url)) return ""
        return ApiMod.Api.server_url.url(ApiMod.Api.server_url.serverUrl, "calibrate", "label", folder, camId)
    }

    function httpUrl(parts) {
        if (!(ApiMod.Api && ApiMod.Api.server_url)) return ""
        return ApiMod.Api.server_url.url.apply(ApiMod.Api.server_url, parts)
    }

    function mappingRemoteUrl(folder, fileName) {
        if (!folder || !fileName) return ""
        const url = httpUrl([ApiMod.Api.server_url.serverUrl, "calibrate", "mapping", folder, fileName])
        return url && url.length ? url : ""
    }

    function cameraRemoteUrl(folder, name, ext) {
        if (!folder || !name) return ""
        const hasExt = name.indexOf(".") !== -1
        const fileName = hasExt ? name : (name + "." + (ext || "jpg"))
        const url = httpUrl([ApiMod.Api.server_url.serverUrl, "calibrate", "image", folder, fileName])
        return url && url.length ? url : ""
    }

    function refreshCameraManage() {
        const data = loadJson(cameraManagePath(currentFolder)) || {}
        cameraManageData = data
        const groups = data && data.group ? data.group : {}
        const lines = []
        Object.keys(groups).forEach((lineKey) => {
            const block = groups[lineKey] || {}
            const list = (block.group || []).map((g) => ({
                                                        key: g.key || "",
                                                        msg: g.msg || "",
                                                        priority: g.priority !== undefined ? g.priority : "",
                                                        cameraList: normalizeCameraList(g.camera_list || []),
                                                        raw: g
                                                    }))
            lines.push({
                           lineKey: lineKey,
                           camera_list: block.camera_list || [],
                           groupList: list
                       })
        })
        lines.sort((a, b)=> a.lineKey.localeCompare(b.lineKey))
        lineGroupList = lines
        if (!selectedGroupKey || !findGroup(selectedGroupKey)) {
            const first = lines.length && lines[0].groupList.length ? lines[0].groupList[0].key : ""
            selectedGroupKey = first
        } else {
            applySelectedGroup()
        }
    }

    function normalizeCameraList(list_) {
        const res = []
        for (let i = 0; i < list_.length; ++i) {
            const entry = list_[i]
            if (typeof entry === "string") {
                res.push({ camera: entry, label: entry })
            } else if (entry && entry.camera) {
                res.push({ camera: entry.camera, label: entry.camera, shape: entry.shape || "Area" })
            }
        }
        return res
    }

    function findGroup(key) {
        if (!key) return null
        for (let i = 0; i < lineGroupList.length; ++i) {
            const groups = lineGroupList[i].groupList || []
            for (let j = 0; j < groups.length; ++j) {
                if (groups[j].key === key) return groups[j].raw || groups[j]
            }
        }
        return null
    }

    function applySelectedGroup() {
        const group = findGroup(selectedGroupKey)
        selectedGroup = group || ({})
        if (!group) {
            mappingObjects = []
            cameraRadioList = []
            objectSettings = []
            perspectiveImageSource = ""
            cameraImageSource = ""
            return
        }
        cameraRadioList = normalizeCameraList(group.camera_list || [])
        objectSettings = buildObjectSettings(group)
        if (!selectedCameraId || !cameraExists(selectedCameraId)) {
            selectedCameraId = cameraRadioList.length ? cameraRadioList[0].camera : ""
        } else {
            refreshCameraImage()
        }
        loadMappingForGroup()
    }

    function cameraExists(cameraId) {
        return cameraRadioList.some((entry)=> entry.camera === cameraId)
    }

    function buildObjectSettings(group) {
        const res = []
        const list = normalizeCameraList(group.camera_list || [])
        const sizeList = group.size_list || []
        for (let i = 0; i < list.length; ++i) {
            const cam = list[i]
            const size = sizeList[i] || []
            res.push({
                         camera: cam.camera,
                         direction: group.direction ? group.direction : "默认",
                         width: size.length > 0 ? size[0] : 0,
                         height: size.length > 1 ? size[1] : 0
                     })
        }
        return res
    }

    function loadMappingForGroup() {
        if (!selectedGroupKey || !currentFolder) {
            mappingObjects = []
            perspectiveImageSource = ""
            return
        }
        const xmlText = loadText(mappingFilePath(currentFolder, selectedGroupKey, "xml"))
        if (!xmlText || !xmlText.length) {
            mappingObjects = []
            perspectiveImageSource = ""
            mappingMeta = ({})
            return
        }
        const parsed = parseMappingXml(xmlText)
        mappingMeta = parsed.meta
        mappingObjects = parsed.objects
        mappingImageWidth = parsed.meta.width || 1
        mappingImageHeight = parsed.meta.height || 1
        const imgName = parsed.meta.filename && parsed.meta.filename.length ? parsed.meta.filename : (selectedGroupKey + ".jpg")
        perspectiveImageSource = mappingRemoteUrl(currentFolder, imgName)
    }

    function parseTag(block, tag) {
        if (!block) return ""
        const exp = new RegExp("<" + tag + ">([\\s\\S]*?)<\\/" + tag + ">", "i")
        const match = exp.exec(block)
        return match ? match[1].trim() : ""
    }

    function parseMappingXml(text) {
        const meta = {
            folder: parseTag(text, "folder"),
            filename: parseTag(text, "filename"),
            path: parseTag(text, "path"),
            database: parseTag(text, "database"),
            width: parseInt(parseTag(text, "width")) || 1,
            height: parseInt(parseTag(text, "height")) || 1,
            depth: parseInt(parseTag(text, "depth")) || 3
        }
        const colors = ["#ff5252", "#8bc34a", "#03a9f4", "#ffb74d", "#cddc39", "#9c27b0", "#ff9800"]
        const objs = []
        const pattern = /<object>([\s\S]*?)<\/object>/gi
        let match
        while ((match = pattern.exec(text)) !== null) {
            const chunk = match[1]
            const name = parseTag(chunk, "name") || ("obj_" + objs.length)
            const xmin = parseFloat(parseTag(chunk, "xmin")) || 0
            const ymin = parseFloat(parseTag(chunk, "ymin")) || 0
            const xmax = parseFloat(parseTag(chunk, "xmax")) || 0
            const ymax = parseFloat(parseTag(chunk, "ymax")) || 0
            objs.push({
                         name: name,
                         xmin: xmin,
                         ymin: ymin,
                         xmax: xmax,
                         ymax: ymax,
                         color: colors[objs.length % colors.length]
                     })
        }
        return { meta: meta, objects: objs }
    }

    function refreshCameraImage() {
        if (!selectedCameraId || !currentFolder) {
            cameraImageSource = ""
            labelImagePath = ""
            return
        }
        const imgName = labelImagePath && labelImagePath.length ? labelImagePath : selectedCameraId
        cameraImageSource = cameraRemoteUrl(currentFolder, imgName, "jpg")
    }

    function loadLabelForCamera(camId) {
        if (!camId || !currentFolder) {
            labelShapes = []
            labelMeta = ({})
            labelImageWidth = 1
            labelImageHeight = 1
            labelImagePath = ""
            return
        }
        const url = labelFilePath(currentFolder, camId)
        const data = loadJson(url) || {}
        labelMeta = data
        labelShapes = data.shapes || []
        labelImageWidth = data.imageWidth || 1
        labelImageHeight = data.imageHeight || 1
        labelImagePath = data.imagePath || ""
        refreshCameraImage()
    }

    function cameraOrderForCurrent() {
        if (!selectedCameraId) return []
        const parts = selectedCameraId.split("_")
        const lineKey = parts.length ? parts[0] : ""
        const lineBlock = (cameraManageData && cameraManageData.group && cameraManageData.group[lineKey]) ? cameraManageData.group[lineKey] : {}
        const orderMap = lineBlock.camera_order || {}
        const order = orderMap[selectedCameraId] || []
        if (order && order.length) return order
        return ["tl", "tr", "br", "bl"]
    }

    function cameraSizeForCurrent() {
        const fallback = { width: labelImageWidth, height: labelImageHeight }
        if (!selectedGroup || !selectedCameraId) return fallback
        const list = selectedGroup.camera_list || []
        const idx = list.indexOf ? list.indexOf(selectedCameraId) : -1
        const sizeList = selectedGroup.size_list || []
        const size = (idx >= 0 && idx < sizeList.length) ? sizeList[idx] : null
        if (size && size.length >= 2) {
            return { width: size[0], height: size[1] }
        }
        return fallback
    }

    function updateMappingObject(index, rect) {
        if (index < 0 || index >= mappingObjects.length) return
        const updated = mappingObjects.slice()
        updated[index] = Object.assign({}, updated[index], rect)
        mappingObjects = updated
    }

    function updateLabelPoint(shapeIndex, pointIndex, newX, newY) {
        //这样不对视图刷新
        if (shapeIndex < 0 || shapeIndex >= labelShapes.length) return
        const shapes = labelShapes
        const shape = Object.assign({}, shapes[shapeIndex])
        const pts = (shape.points || [])
        if (pointIndex < 0 || pointIndex >= pts.length) return
        pts[pointIndex] = [newX, newY]

        labelShapes = shapes
    }

    function updateLabelPointEnd(shapeIndex, pointIndex, newX, newY) {
        //对视图刷新
        if (shapeIndex < 0 || shapeIndex >= labelShapes.length) return
        const shapes = labelShapes.slice()
        const shape = Object.assign({}, shapes[shapeIndex])
        const pts = (shape.points || []).slice()
        if (pointIndex < 0 || pointIndex >= pts.length) return
        pts[pointIndex] = [newX, newY]
        shape.points = pts
        shapes[shapeIndex] = shape
        labelShapes = shapes
    }

    function updateObjectSetting(index, key, value) {
        if (index < 0 || index >= objectSettings.length) return
        const updated = objectSettings.slice()
        updated[index] = Object.assign({}, updated[index], { [key]: value })
        objectSettings = updated
    }

    function buildMappingXml() {
        const meta = mappingMeta || {}
        const lines = []
        lines.push("<annotation>")
        lines.push(`\t<folder>${meta.folder || "mapping"}</folder>`)
        lines.push(`\t<filename>${meta.filename || (selectedGroupKey + ".jpg")}</filename>`)
        lines.push(`\t<path>${meta.path || ""}</path>`)
        lines.push("\t<source>")
        lines.push(`\t\t<database>${meta.database || "Unknown"}</database>`)
        lines.push("\t</source>")
        lines.push("\t<size>")
        lines.push(`\t\t<width>${mappingImageWidth}</width>`)
        lines.push(`\t\t<height>${mappingImageHeight}</height>`)
        lines.push(`\t\t<depth>${meta.depth || 3}</depth>`)
        lines.push("\t</size>")
        lines.push("\t<segmented>0</segmented>")
        mappingObjects.forEach((obj)=>{
            lines.push("\t<object>")
            lines.push(`\t\t<name>${obj.name}</name>`)
            lines.push("\t\t<pose>Unspecified</pose>")
            lines.push("\t\t<truncated>0</truncated>")
            lines.push("\t\t<difficult>0</difficult>")
            lines.push("\t\t<bndbox>")
            lines.push(`\t\t\t<xmin>${Math.round(obj.xmin)}</xmin>`)
            lines.push(`\t\t\t<ymin>${Math.round(obj.ymin)}</ymin>`)
            lines.push(`\t\t\t<xmax>${Math.round(obj.xmax)}</xmax>`)
            lines.push(`\t\t\t<ymax>${Math.round(obj.ymax)}</ymax>`)
            lines.push("\t\t</bndbox>")
            lines.push("\t</object>")
        })
        lines.push("</annotation>")
        return lines.join("\n")
    }

    function saveLabelForCamera(callback) {
        if (!selectedCameraId || !currentFolder) {
            statusMessage = qsTr("请选择相机")
            return
        }
        const payload = {
            calibrate: currentFolder,
            camera: selectedCameraId,
            data: Object.assign({}, labelMeta, {
                                     shapes: labelShapes,
                                     imageWidth: labelImageWidth,
                                     imageHeight: labelImageHeight,
                                 })
        }
        if (ApiMod.Api && ApiMod.Api.save_calibrate_label) {
            busy = true
            ApiMod.Api.save_calibrate_label(payload,
                                            function(resp){
                                                busy = false
                                                statusMessage = qsTr("标注已保存")
                                                if (callback) callback(true, resp)
                                            },
                                            function(err){
                                                busy = false
                                                statusMessage = qsTr("标注保存失败")
                                                console.warn("save_calibrate_label error", err)
                                                if (callback) callback(false, err)
                                            })
        } else {
            console.warn("save_calibrate_label api missing", payload)
            statusMessage = qsTr("缺少标注保存接口")
            if (callback) callback(false, "api missing")
        }
    }

    function saveCurrentMapping(callback) {
        if (!currentFolder || !selectedGroupKey) {
            statusMessage = "请选择有效的标定分组"
            return
        }
        const payload = {
            folder: currentFolder,
            group: selectedGroupKey,
            xml: buildMappingXml(),
            objects: mappingObjects,
            meta: mappingMeta
        }
        if (ApiMod.Api && ApiMod.Api.save_calibrate_mapping) {
            busy = true
            ApiMod.Api.save_calibrate_mapping(payload,
                                              function(resp){
                                                  busy = false
                                                  statusMessage = qsTr("标注已保存")
                                                  if (callback) callback(true, resp)
                                              },
                                              function(err){
                                                  busy = false
                                                  statusMessage = qsTr("保存失败")
                                                  if (callback) callback(false, err)
                                              })
        } else {
            console.warn("save_calibrate_mapping api missing, xml dump:", payload.xml)
            statusMessage = qsTr("缺少保存接口，已在日志中输出 XML")
        }
    }

    function saveObjectSettings(callback) {
        if (!currentFolder || !selectedGroupKey) {
            statusMessage = "请选择有效的标定分组"
            return
        }
        const payload = {
            folder: currentFolder,
            group: selectedGroupKey,
            settings: objectSettings
        }
        if (ApiMod.Api && ApiMod.Api.save_calibrate_group) {
            busy = true
            ApiMod.Api.save_calibrate_group(payload,
                                            function(resp){
                                                busy = false
                                                statusMessage = qsTr("对象配置已保存")
                                                if (callback) callback(true, resp)
                                            },
                                            function(err){
                                                busy = false
                                                statusMessage = qsTr("对象配置保存失败")
                                                if (callback) callback(false, err)
                                            })
        } else {
            console.warn("save_calibrate_group api missing", payload)
            statusMessage = qsTr("缺少对象保存接口")
        }
    }

    function captureCurrentCamera(callback) {
        if (!selectedCameraId) {
            statusMessage = qsTr("请选择相机")
            return
        }
        if (!(ApiMod.Api && ApiMod.Api.capture_calibrate_camera)) {
            statusMessage = qsTr("缺少采集接口")
            return
        }
        busy = true
        ApiMod.Api.capture_calibrate_camera({
                                                folder: currentFolder,
                                                camera: selectedCameraId
                                            },
                                            function(resp){
                                                busy = false
                                                statusMessage = qsTr("采集完成")
                                                refreshCameraImage()
                                                if (callback) callback(true, resp)
                                            },
                                            function(err){
                                                busy = false
                                                statusMessage = qsTr("采集失败")
                                                if (callback) callback(false, err)
                                            })
    }

    function saveCapturedImages(callback) {
        if (!(ApiMod.Api && ApiMod.Api.save_calibrate_capture)) {
            statusMessage = qsTr("缺少保存采集接口")
            return
        }
        busy = true
        ApiMod.Api.save_calibrate_capture({
                                              folder: currentFolder
                                          },
                                          function(resp){
                                              busy = false
                                              statusMessage = qsTr("采集结果已保存")
                                              if (callback) callback(true, resp)
                                          },
                                          function(err){
                                              busy = false
                                              statusMessage = qsTr("保存采集失败")
                                              if (callback) callback(false, err)
                                          })
    }

    function refreshPerspective(callback) {
        loadMappingForGroup()
        if (ApiMod.Api && ApiMod.Api.refresh_calibrate_perspective) {
            ApiMod.Api.refresh_calibrate_perspective({
                                                         folder: currentFolder,
                                                         group: selectedGroupKey
                                                     },
                                                     function(resp){
                                                         if (callback) callback(true, resp)
                                                     },
                                                     function(err){
                                                         if (callback) callback(false, err)
                                                     })
        }
    }

    function setAutoRefresh(flag) {
        autoRefresh = flag
    }

    function setStatus(msg) {
        statusMessage = msg
    }

    function createFolder(options, callback) {
        if (!options || !options.name) {
            statusMessage = qsTr("请输入有效名称")
            return
        }
        if (folderList.some((item)=> item.toLowerCase() === options.name.toLowerCase())) {
            statusMessage = qsTr("名称重复")
            if (callback) callback(false, "dup")
            return
        }
        if (!(ApiMod.Api && ApiMod.Api.create_calibrate_folder)) {
            statusMessage = qsTr("缺少创建接口")
            return
        }
        busy = true
        ApiMod.Api.create_calibrate_folder(options,
                                           function(resp){
                                               busy = false
                                               statusMessage = qsTr("已创建标定文件夹")
                                               refreshFolders()
                                               if (callback) callback(true, resp)
                                           },
                                           function(err){
                                               busy = false
                                               statusMessage = qsTr("创建失败")
                                               if (callback) callback(false, err)
                                           })
    }

    function deleteFolder(name, callback) {
        if (!name) return
        if (!(ApiMod.Api && ApiMod.Api.delete_calibrate_folder)) {
            statusMessage = qsTr("缺少删除接口")
            return
        }
        busy = true
        ApiMod.Api.delete_calibrate_folder({ name: name },
                                           function(resp){
                                               busy = false
                                               statusMessage = qsTr("已删除")
                                               refreshFolders()
                                               if (name === currentFolder) currentFolder = ""
                                               if (callback) callback(true, resp)
                                           },
                                           function(err){
                                               busy = false
                                               statusMessage = qsTr("删除失败")
                                               if (callback) callback(false, err)
                                           })
    }

    function useFolder(name, callback) {
        if (!name) return
        if (!(ApiMod.Api && ApiMod.Api.use_calibrate_folder)) {
            currentFolder = name
            statusMessage = qsTr("缺少接口，已切换本地视图")
            return
        }
        busy = true
        ApiMod.Api.use_calibrate_folder({ name: name },
                                        function(resp){
                                            busy = false
                                            currentFolder = name
                                            statusMessage = qsTr("已切换")
                                            if (callback) callback(true, resp)
                                        },
                                        function(err){
                                            busy = false
                                            statusMessage = qsTr("切换失败")
                                            if (callback) callback(false, err)
                                        })
    }

    Component.onCompleted: {
        rebuildFolderList()
    }
}
