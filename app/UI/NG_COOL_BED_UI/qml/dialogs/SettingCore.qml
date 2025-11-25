import QtQuick

QtObject {
    id: core

    // 常规
    property string serverUrl: "http://127.0.0.1:8000"
    property string ipAddress: "192.168.0.100"
    property string modelType: "默认"
    property string configPath: "config/calibrate/calibrate.json"
    property string currentConfig: "calibrate1124"

    property var modelCategories: ["目标检测", "分割"]
    property string selectedCategory: modelCategories[0]
    property var modelListDet: ["det_model_a", "det_model_b"]
    property var modelListSeg: ["seg_model_a", "seg_model_b"]
    property string selectedModel: modelListDet[0]

    // 测试
    property string testDataFolder: "data/tests"
}
