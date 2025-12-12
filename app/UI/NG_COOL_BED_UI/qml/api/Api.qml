pragma Singleton
import QtQuick

Item {

    property Ajax ajax: Ajax{}
    property ServerUrl server_url: ServerUrl{}
    function calibrateUrl() {
        var parts = [server_url.serverUrl, "calibrate"]
        for (var i = 0; i < arguments.length; ++i) {
            parts.push(arguments[i])
        }
        return server_url.url.apply(server_url, parts)
    }

    function get_info(success, failure){
        return ajax.get(server_url.url(server_url.serverUrl,"info"),success, failure)
    }

    function get_map(cool_bed_key ,success, failure){
        // 兼容未传 key 的旧调用：第一个参数若为函数，则当作 success 回调
        if (typeof cool_bed_key === "function") {
            failure = success
            success = cool_bed_key
            cool_bed_key = null
        }
        const url = cool_bed_key ?
                    server_url.url(server_url.serverUrl,"map",cool_bed_key) :
                    server_url.url(server_url.serverUrl,"map")
        return ajax.get(url,success, failure)
    }

    function get_image_url(cool_bed_key, key, index, show_mask){
        return server_url.url(server_url.serverUrl, "image",cool_bed_key, key, index,parseInt(show_mask+0))
    }

    function get_video_url(cool_bed_key, key, show_mask, token){
        var base = server_url.url(server_url.serverUrl, "video", cool_bed_key, key, parseInt(show_mask+0))
        if (token === undefined || token === null) {
            return base
        }
        var sep = base.indexOf("?") === -1 ? "?" : "&"
        return base + sep + "t=" + token
    }

    function get_data(cool_bed_key, success, failure){
        return ajax.get(server_url.url(server_url.serverUrl,"data",cool_bed_key),success, failure)
    }

    function get_send_data(success, failure){
        return ajax.get(server_url.url(server_url.serverUrl, "send_data"), success, failure)
    }

    function test_pre_image(success, failure){
        return ajax.get(server_url.url(server_url.serverUrl, "test_pre_image"), success, failure)
    }

    function test_next_image(success, failure){
        return ajax.get(server_url.url(server_url.serverUrl, "test_next_image"), success, failure)
    }

    function get_cameras(success, failure){
        // 相机信息表：拍摄冷床、IP、rtsp_url、序号、位置
        return ajax.get(server_url.url(server_url.serverUrl, "cameras"), success, failure)
    }


    function save_cap(success, failure){
        return ajax.get(server_url.url(server_url.serverUrl, "save_cap"), success, failure)
    }

    function save_one_cap(success, failure){
        return ajax.get(server_url.url(server_url.serverUrl, "save_one_cap"), success, failure)
    }

    function get_opencv_display(success, failure) {
        return ajax.get(server_url.url(server_url.serverUrl, "debug", "opencv_display"), success, failure)
    }

    function set_opencv_display(enable, success, failure) {
        return ajax.post(
                    server_url.url(server_url.serverUrl, "debug", "opencv_display"),
                    { "enable": !!enable },
                    success,
                    failure)
    }

    function get_predict_display(success, failure) {
        return ajax.get(server_url.url(server_url.serverUrl, "debug", "predict_display"), success, failure)
    }

    function set_predict_display(enable, success, failure) {
        return ajax.post(
                    server_url.url(server_url.serverUrl, "debug", "predict_display"),
                    { "enable": !!enable },
                    success,
                    failure)
    }

    function get_calibrate_folders(success, failure) {
        return ajax.get(calibrateUrl("folders"), success, failure)
    }

    function create_calibrate_folder(payload, success, failure) {
        return ajax.post(calibrateUrl("folders"), payload, success, failure)
    }

    function delete_calibrate_folder(payload, success, failure) {
        return ajax.post(calibrateUrl("folders", "delete"), payload, success, failure)
    }

    function use_calibrate_folder(payload, success, failure) {
        return ajax.post(calibrateUrl("folders", "use"), payload, success, failure)
    }

    function save_calibrate_mapping(payload, success, failure) {
        return ajax.post(calibrateUrl("mapping", "save"), payload, success, failure)
    }

    function save_calibrate_group(payload, success, failure) {
        return ajax.post(calibrateUrl("group", "save"), payload, success, failure)
    }

    function save_calibrate_label(payload, success, failure) {
        return ajax.post(calibrateUrl("label", "save"), payload, success, failure)
    }

    function capture_calibrate_camera(payload, success, failure) {
        return ajax.post(calibrateUrl("capture"), payload, success, failure)
    }

    function save_calibrate_capture(payload, success, failure) {
        return ajax.post(calibrateUrl("capture", "save"), payload, success, failure)
    }

    function refresh_calibrate_perspective(payload, success, failure) {
        return ajax.post(calibrateUrl("perspective", "refresh"), payload, success, failure)
    }

    function get_alg_models(success, failure) {
        return ajax.get(server_url.url(server_url.serverUrl, "alg", "models"), success, failure)
    }

    function start_alg_test(payload, success, failure) {
        return ajax.post(server_url.url(server_url.serverUrl, "alg", "test", "start"), payload, success, failure)
    }

    function stop_alg_test(payload, success, failure) {
        return ajax.post(server_url.url(server_url.serverUrl, "alg", "test", "stop"), payload, success, failure)
    }

    function get_priority_status(success, failure) {
        return ajax.get(server_url.url(server_url.serverUrl, "priority", "status"), success, failure)
    }

    function set_group_shield(payload, success, failure) {
        return ajax.post(server_url.url(server_url.serverUrl, "priority", "shield"), payload, success, failure)
    }
}
