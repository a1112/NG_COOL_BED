import QtQuick

Item {

    property int draw_width
    property int draw_height

    property var data: map_config.map_data[cool_bed_core.current_key]
    property int image_width: data["width"]
    property int image_height: data["height"]

    property real x_asp: draw_width   / image_width
    property real y_asp: draw_height / image_height

    property rect up:Qt.rect(
                        up_rect[0]*x_asp,
                        up_rect[1]*y_asp,
                        up_rect[2]*x_asp,
                        up_rect[3]*y_asp,
                        )

    property var up_rect: data["up"]

    property rect down:Qt.rect(
                        down_rect[0]*x_asp,
                        down_rect[1]*y_asp,
                        down_rect[2]*x_asp,
                        down_rect[3]*y_asp,
                        )


    property var down_rect: data["down"]

    property rect cool_bed:Qt.rect(
                        cool_bed_rect[0]*x_asp,
                        cool_bed_rect[1]*y_asp,
                        cool_bed_rect[2]*x_asp,
                        cool_bed_rect[3]*y_asp,
                        )
    property var cool_bed_rect: data["cool_bed"]


    function get_rect(x,y,w,h){
        return Qt.rect(
                        x*x_asp,
                        y*y_asp,
                        w*x_asp,
                        h*y_asp,
                    )
    }

    // "roll_width_mm":self.roll_width,
    // "roll_height_mm":self.roll_height,
    // "up_seat_height_mm":self.up_seat_height,
    // "down_seat_height_mm":self.down_seat_height,
    // "roll_count":self.roll_count,
    // "cool_bed_width_mm":self.cool_bed_width,
    // "cool_bed_height_mm":self.cool_bed_height,
    // "up_seat_d_mm":self.up_seat_d,
    // "up_seat_u_mm":self.up_seat_u,
    // "up_cool_bed_mm":self.up_cool_bed,
    // "center_x":self.center_x

        property real roll_width_mm: data["roll_width_mm"]
        property real roll_height_mm: data["roll_height_mm"]
        property real up_seat_height_mm: data["up_seat_height_mm"]
        property real down_seat_height_mm: data["down_seat_height_mm"]
        property int roll_count: data["roll_count"]
        property real cool_bed_width_mm: data["cool_bed_width_mm"]
        property real cool_bed_height_mm: data["cool_bed_height_mm"]
    property real y_mm_asp:  cool_bed.height/cool_bed_height_mm

        property real up_seat_d_mm: data["up_seat_d_mm"]
        property real up_seat_u_mm: data["up_seat_u_mm"]
        property real up_cool_bed_mm: data["up_cool_bed_mm"]
        property real center_x_mm: data["center_x_mm"]
}
