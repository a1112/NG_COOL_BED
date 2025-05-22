import QtQuick

Item {

    property string server_ip: "127.0.0.1"
    property int server_port: 8001


    property var lastUrls:{return {}}

    function getLastUrlByKey(key){
        return lastUrls[key]
    }

    readonly property string protocol: "http://"
    readonly property string ws_protocol:"ws://"

    readonly property string serverUrl: protocol+hostname+":"+port
    readonly property string wsServerUrl: ws_protocol+hostname+":"+port

    readonly property string hostname:server_ip
    readonly property int port: server_port



    function url(reUrl,...args){
        let key =""

        for(let argIndex in args){
            key=args[0]
            if (typeof(args[argIndex])=='object')
            {
                reUrl+=getGetArgs(args[argIndex])
            }
            else{
            reUrl+="/"+args[argIndex]
                }
        }
        lastUrls[key]=reUrl
        return reUrl
    }


    function getPostArgs(dictData){
        let res=""
        for(let key in dictData){
            if(res){
                res+="&"
            }
            res+=key+"="+dictData[key]
        }
        return res
    }


    function getGetArgs(dictData){
        let res=""
        for(let key in dictData){
            if(res){
                res+="&"
            }
            else{
            res+="?"
            }
            res+=key+"="+dictData[key]
        }
        return res
    }
}
