import QtQuick
import QtQuick.Controls.Material

Menu {
    id: root
    width: 630
    height: 800

    property var db6_data: { return {}}
    property string db6_byte: ""

    onDb6_dataChanged: {
        for (let key in db6_data) {
            let has_data = false
            for (let i = 0; i < dataModel.count; i++) {
                if (dataModel.get(i).title === key) {
                    dataModel.setProperty(i, "value", "" + db6_data[key])
                    has_data = true
                    break
                }
            }
            if (!has_data) {
                dataModel.append({
                                     "title": key,
                                     "value": "" + db6_data[key]
                                 })
            }
        }
    }

    property ListModel dataModel: ListModel {}

    Flow {
        anchors.fill: parent
        Repeater {
            anchors.fill: parent
            model: dataModel
            TextViewItem { }
        }

        Label {
            width: parent.width
            height: 50
            text: db6_byte
            wrapMode: Text.WrapAnywhere
        }
    }

    function open_() {
        root.popup()
    }
}

