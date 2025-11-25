pragma Singleton
import QtQuick

Item {

    property Ajax ajax: Ajax{}
    property ServerUrl server_url: ServerUrl{}


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
}
