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

    property bool i_left: in_left
    property bool i_right: in_right
    property bool i_cool_bed: in_cool_bed
    property bool i_roll: in_roll
    property bool c_to_roll_center_y: to_roll_center_y

    // "in_left": self.in_left,
    // "in_right": self.in_right,
    // "in_cool_bed": self.in_cool_bed,
    // "in_roll": self.in_roll,
    // "to_roll_center_y": self.to_roll_center_y

    function get_vis_str(){

        return "x: "+(m_x/1000)+" y: "+(m_y/1000)+" w: "+(m_w/1000) + " h: "+ (m_h/1000)
    }

    function get_info_str(){
            return "左："+i_left+" 右:"+i_right+" 冷床:"+i_cool_bed+" 辊道:"+i_roll+" 距离中心:"+c_to_roll_center_y
    }
    function get_in_item_str(it){
        return it?"<font color=\"green\">T</font>":"<font color=\"red\">F</font>"
    }
    property string in_str1:get_in_item_str(i_left && i_cool_bed) +" "+get_in_item_str(i_right && i_cool_bed)
    property string in_str2:get_in_item_str(i_left && i_roll)+" " +get_in_item_str(i_right && i_roll)
    // property string in_str:"l:"+get_in_item_str(i_left)+"r:"+get_in_item_str(i_right)+
    //                        "co:"+get_in_item_str(i_cool_bed)+"ro:"+get_in_item_str(i_roll)
    property string type_name: "base"
    property string vis_str: get_vis_str(type_name)

    property string info_str: get_info_str()

    property real y_t_c :  (m_y-m_h/2 -5000/2)/1000
}
