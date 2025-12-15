import QtQuick
import QtQuick.Controls.Material

Menu {
    id:root
    width: 630
    height: 800



    property var send_data: { return {}}
    property string send_byte: ""
    property real plcLastWriteOkTs: 0
    property int plcLastWriteOkBefore01s: -1

    Timer {
        interval: 100
        repeat: true
        running: root.visible
        onTriggered: {
            if (plcLastWriteOkTs > 0) {
                plcLastWriteOkBefore01s = Math.max(
                            0,
                            Math.floor(((Date.now() / 1000.0) - plcLastWriteOkTs) * 10))
            } else {
                plcLastWriteOkBefore01s = -1
            }
        }
    }
    onSend_dataChanged: {
      for (let key in send_data){
        let has_data=false
        for (let i=0;i<dataModel.count;i++){
            if (dataModel.get(i).title === key)
            {
                dataModel.setProperty(i,"value",""+send_data[key])
                has_data=true
                break
            }

        }
        if (!has_data){
            dataModel.append({
                             "title":key,
                             "value": "" + send_data[key]
                             })

        }
      }


    }

    property ListModel dataModel: ListModel{}
    Flow{
        anchors.fill: parent
        Label {
            width: parent.width
            height: 30
            text: plcLastWriteOkBefore01s < 0
                  ? qsTr("最后一次PLC写入成功: --")
                  : qsTr("最后一次PLC写入成功: %1 (0.1s)").arg(plcLastWriteOkBefore01s)
        }
        Repeater{
            anchors.fill: parent
            model: dataModel
            TextViewItem{
            }

        }

        Label {
            width: parent.width
            height: 50
            id: name
            text: send_byte
            wrapMode:Text.WrapAnywhere
        }
    }


    function open_(){
        root.popup()
    }
}
