import QtQuick

Item {

    function key_to_msg(key){
        if (key === "VERSION"){
            return "版本"
        }
        if (key === "I_NAI_W0_ALV_CNT"){
            return "心跳"
        }
        if (key==="I_NAI_MET_F1"){
            return "F1辊道（一号冷床左半段辊道）有钢"
        }
        if (key==="I_NAI_MET_F2"){
            return "F2辊道（一号冷床右半段辊道）有钢"
        }
        if (key==="I_NAI_MET_F5"){
            return "F5辊道（二号冷床左半段辊道）有钢"
        }
        if (key==="I_NAI_MET_F6"){
            return "F6辊道（二号冷床右半段辊道）有钢"
        }
        if (key==="I_NAI_LONG_CB1"){
            return "保留"
        }
        if (key==="I_NAI_LONG_CB2"){
            return "保留"
        }
        if (key==="I_NAI_ERROR_CB1"){
            return "一号冷床识别系统故障"
        }
        if (key==="I_NAI_ERROR_CB2"){
            return "二号冷床识别系统故障"
        }
        if (key==="I_NAI_LONG_F12"){
            return "保留2"
        }
        if (key==="I_NAI_LONG_F56"){
            return "保留2"
        }


        if (key==="I_NAI_W1_spare1"){
            return "一号冷床左半段有钢"
        }
        if (key==="I_NAI_W1_spare2"){
            return "一号冷床右半段有钢"
        }
        if (key==="I_NAI_W1_spare3"){
            return "二号冷床左半段有钢"
        }
        if (key==="I_NAI_W1_spare4"){
            return "二号冷床右半段有钢"
        }
        if (key==="I_NAI_W1_spare5"){
            return "保留3"
        }
        if (key==="I_NAI_W1_spare6"){
            return "保留3"
        }


        if (key==="I_NAI_X_dis_CB1G3"){
            return "一号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 x"
        }
        if (key==="I_NAI_Y_dis_CB1G3"){
            return "一号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 y"
        }
        if (key==="I_NAI_Len_CB1G3"){
            return "一号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 w"
        }
        if (key==="I_NAI_Wid_CB1G3"){
            return "一号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 h"
        }
        if (key==="I_NAI_Ang_CB1G3"){
            return "一号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 角度"
        }


        if (key==="I_NAI_X_dis_CB1G4"){
            return "一号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 x"
        }
        if (key==="I_NAI_Y_dis_CB1G4"){
            return "一号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 y"
        }
        if (key==="I_NAI_Len_CB1G4"){
            return "一号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 w"
        }
        if (key==="I_NAI_Wid_CB1G4"){
            return "一号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 h"
        }
        if (key==="I_NAI_Ang_CB1G4"){
            return "一号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 角度"
        }



        if (key==="I_NAI_X_dis_CB2G3"){
            return "二号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 x"
        }
        if (key==="I_NAI_Y_dis_CB2G3"){
            return "二号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 y"
        }
        if (key==="I_NAI_Len_CB2G3"){
            return "二号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 w"
        }
        if (key==="I_NAI_Wid_CB2G3"){
            return "二号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 h"
        }
        if (key==="I_NAI_Ang_CB2G3"){
            return "二号冷床左半段冷床上最下边缘板子距离下轴承座上边缘的位置 角度"
        }


        if (key==="I_NAI_X_dis_CB2G4"){
            return "二号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 x"
        }
        if (key==="I_NAI_Y_dis_CB2G4"){
            return "二号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 y"
        }
        if (key==="I_NAI_Len_CB2G4"){
            return "二号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 w"
        }
        if (key==="I_NAI_Wid_CB2G4"){
            return "二号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 h"
        }
        if (key==="I_NAI_Ang_CB2G4"){
            return "二号冷床右半段冷床上最下边缘板子距离下轴承座上边缘的位置 角度"
        }


        if (key==="I_NAI_Y_dis_F1"){
            return "F1辊道（一号冷床左半段辊道）辊道上板子的位置，板子中心跟辊道中心线的偏离值"
        }
        if (key==="I_NAI_Ang_F1"){
            return "F1辊道（一号冷床左半段辊道）辊道上板子的倾斜程度"
        }
        if (key==="I_NAI_Y_dis_F2"){
            return "F2辊道（一号冷床右半段辊道）辊道上板子的位置，板子中心跟辊道中心线的偏离值"
        }
        if (key==="I_NAI_Ang_F2"){
            return "F2辊道（一号冷床右半段辊道）辊道上板子的倾斜程度"
        }
        if (key==="I_NAI_Y_dis_F5"){
            return "F5辊道（二号冷床左半段辊道）辊道上板子的位置，板子中心跟辊道中心线的偏离值"
        }
        if (key==="I_NAI_Ang_F5"){
            return "F5辊道（二号冷床左半段辊道）辊道上板子的倾斜程度"
        }
        if (key==="I_NAI_Y_dis_F6"){
            return "F6辊道（二号冷床右半段辊道）辊道上板子的位置，板子中心跟辊道中心线的偏离值"
        }
        if (key==="I_NAI_Ang_F6"){
            return "F6辊道（二号冷床右半段辊道）辊道上板子的倾斜程度"
        }

        if (key==="I_NAI_W30_spare"){
            return "I_NAI_W30_spare"
        }
        if (key==="I_NAI_W31_spare"){
            return "I_NAI_W31_spare"
        }
    }

}
