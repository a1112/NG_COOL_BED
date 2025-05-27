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


}
