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

    function get_image_url(cool_bed_key, key, index){
        return server_url.url(server_url.serverUrl, "image",cool_bed_key, key, index)
    }

    function get_data(cool_bed_key, success, failure){
        return ajax.get(server_url.url(server_url.serverUrl,"data",cool_bed_key),success, failure)
    }

    function get_send_data(success, failure){
        return ajax.get(server_url.url(server_url.serverUrl, "send_data"), success, failure)
    }
}
