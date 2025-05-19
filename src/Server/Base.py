from fastapi import FastAPI
from Result.DataItem import DataItem
from ProjectManagement.Business import Business
from Globals import business_main

business_main: Business

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_data_item_info(data:DataItem):
    return {
        "左侧辊道有板":data.has_roll_steel_left,
        "右侧辊道有板":data.has_roll_steel_right,
        "左侧冷床辊道有板":data.has_cool_bed_steel_left,
        "右侧冷床辊道有板":data.has_cool_bed_steel_right,
        "操作错误": data.has_error,
        "左侧距离下辊道距离":data.left_under_steel.y2_mm,
        "左侧距离辊道中心距离": data.left_under_steel.to_roll_center_y,
        "steel_rect":data.steel_info
    }

@app.get("/steel_msg")
def steel_info():
    di1:DataItem = business_main.data_item_l1
    di2:DataItem = business_main.data_item_l2
    return {
        "L1":get_data_item_info(di1),
        "L2":get_data_item_info(di2)
    }

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6110)