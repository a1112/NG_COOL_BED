import QtQuick

Item {
    property var test :{"x_px":307,"y_px":0,"w_px":2700,
                        "h_px":93,"x_mm":4818.897637795276,"y_mm":11495.702702702703,
                        "w_mm":42519.68503937008,"h_mm":1460.3513513513517,"name":"steel"}

    property int p_x: x_px
    property int p_y: y_px
    property int p_w: w_px
    property int p_h: h_px

    property rect rect_: map_config_item.get_rect(p_x,p_y,p_w,p_h)

    property int m_x: parseInt(x_mm)
    property int m_y: parseInt(y_mm)
    property int m_w: parseInt(w_mm)
    property int m_h: parseInt(h_mm)

    property string name_: name
}
