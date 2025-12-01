import QtQuick

Item {
    // 防御空数据
    property var data: (map_config && map_config.map_data && cool_bed_core) ? (map_config.map_data[cool_bed_core.current_key] || {}) : {}

    property int draw_width: 0
    property int draw_height: 0

    property int image_width: (data && data.width) ? data.width : 1
    property int image_height: (data && data.height) ? data.height : 1

    property real x_asp: draw_width  / (image_width || 1)
    property real y_asp: draw_height / (image_height || 1)

    property var up_rect: (data && data.up) ? data.up : [0,0,1,1]
    property rect up: Qt.rect(up_rect[0]*x_asp, up_rect[1]*y_asp, up_rect[2]*x_asp, up_rect[3]*y_asp)

    property var down_rect: (data && data.down) ? data.down : [0,0,1,1]
    property rect down: Qt.rect(down_rect[0]*x_asp, down_rect[1]*y_asp, down_rect[2]*x_asp, down_rect[3]*y_asp)

    property var cool_bed_rect: (data && data.cool_bed) ? data.cool_bed : [0,0,1,1]
    property rect cool_bed: Qt.rect(cool_bed_rect[0]*x_asp, cool_bed_rect[1]*y_asp, cool_bed_rect[2]*x_asp, cool_bed_rect[3]*y_asp)

    function get_rect(x,y,w,h){
        return Qt.rect(x*x_asp, y*y_asp, w*x_asp, h*y_asp)
    }

    property real roll_width_mm: (data && data.roll_width_mm) ? data.roll_width_mm : 0
    property real roll_height_mm: (data && data.roll_height_mm) ? data.roll_height_mm : 0
    property real up_seat_height_mm: (data && data.up_seat_height_mm) ? data.up_seat_height_mm : 0
    property real down_seat_height_mm: (data && data.down_seat_height_mm) ? data.down_seat_height_mm : 0
    property int roll_count: (data && data.roll_count) ? data.roll_count : 0
    property real cool_bed_width_mm: (data && data.cool_bed_width_mm) ? data.cool_bed_width_mm : 1
    property real cool_bed_height_mm: (data && data.cool_bed_height_mm) ? data.cool_bed_height_mm : 1
    property real y_mm_asp: cool_bed.height / (cool_bed_height_mm || 1)

    property real up_seat_d_mm: (data && data.up_seat_d_mm) ? data.up_seat_d_mm : 0
    property real up_seat_u_mm: (data && data.up_seat_u_mm) ? data.up_seat_u_mm : 0
    property real up_cool_bed_mm: (data && data.up_cool_bed_mm) ? data.up_cool_bed_mm : 0
    property real center_x_mm: (data && data.center_x_mm) ? data.center_x_mm : 0
}
