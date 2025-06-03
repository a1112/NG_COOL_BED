import cv2
from fastapi import FastAPI

from Configs.CameraManageConfig import camera_manage_config
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Configs.GroupConfig import GroupConfig
from Configs.MappingConfig import MappingConfig
from ProjectManagement.Main import CoolBedThreadWorker
from Result.DataItem import DataItem
from ProjectManagement.Business import Business
from Globals import business_main, cool_bed_thread_worker_map, global_config
from fastapi.responses import StreamingResponse, FileResponse, Response

from Server.tool import noFindImageByte

business_main: Business

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_data_item_info(data:DataItem):
    if data is None:
        return "w无数据，刷新后再尝试吧。"
    return {
        "key":data.group_key,
        "左侧辊道有板" : data.has_roll_steel_left,
        "右侧辊道有板" : data.has_roll_steel_right,
        "左侧冷床辊道有板" : data.has_cool_bed_steel_left,
        "右侧冷床辊道有板" : data.has_cool_bed_steel_right,
        "操作错误" : data.has_error,
        "左侧距离下辊道距离" : data.left_under_steel.y2_mm,
        "左侧距离辊道中心距离" : data.left_under_steel.to_roll_center_y,
        "steel_rect" : data.steel_info
    }

@app.get("/steel_msg")
def steel_info():
    di1:DataItem = business_main.data_item_l1
    di2:DataItem = business_main.data_item_l2
    return {
        "L1":get_data_item_info(di1),
        "L2":get_data_item_info(di2)
    }


@app.get("/info")
async def get_info():

    return camera_manage_config.info


@app.get("/map/{cool_bed_key:str}")
async def get_map(cool_bed_key):
    cbc:CoolBedGroupConfig = camera_manage_config.group_dict[cool_bed_key]
    re_data = {}
    for g_key,g_config in cbc.groups_dict.items():
        g_config:GroupConfig
        map_config :MappingConfig = g_config.map_config
        re_data[g_key] = map_config.info
    return re_data

@app.get("/image/{cool_bed:str}/{key:str}/{cap_index:int}")
async def get_image(cool_bed:str, key:str, cap_index:int):
    cool_bed_thread_worker = cool_bed_thread_worker_map[cool_bed]
    cool_bed_thread_worker:CoolBedThreadWorker
    index, cv_image = cool_bed_thread_worker.get_image(key)
    if index < 0:
        return Response(content=noFindImageByte, media_type="image/jpg")
    _, encoded_image = cv2.imencode(".jpg", cv_image)
    # 返回图像响应
    return Response(content=encoded_image.tobytes(), media_type="image/jpeg")

@app.get("/data/{cool_bed:str}")
async def get_data(cool_bed:str):
    cool_bed_data =  {key:item.get_info() for key, item in business_main.data_item_dict[cool_bed].items()}
    cool_bed_data["current"] = business_main.get_current_data(cool_bed)
    return cool_bed_data
    #  return business_main.data_map.get_info_by_cool_bed(cool_bed)

@app.get("/send_data")
async def send_data():
    return business_main.send_data

@app.get("/current_info")
def current_info():

    return business_main.current_info



if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6110)