import QtQuick

Item {

    property Ajax ajax: Ajax{}

    property ServerUrl server_url: ServerUrl{}


    function get_info(success, failure){
        return ajax.get(server_url.url(server_url.serverUrl,"info"),success, failure)
    }

    function get_map(cool_bed_keey ,success, failure){
        return ajax.get(server_url.url(server_url.serverUrl,"map",cool_bed_keey),success, failure)
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

}
