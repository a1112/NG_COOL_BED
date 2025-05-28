# 裁决图像
from tqdm import tqdm
from pathlib import Path
from PIL import Image
from_folder = Path(fr"D:\NgDataSave\相机采集保存\join")
out_folder = from_folder.parent/"crop____"
out_folder.mkdir(exist_ok=True, parents=True)
for f_ in tqdm(from_folder.glob(fr"*\*\*.jpg")):
    image = Image.open(f_)
    w,h = image.size


    if "L1_g0_2345" in str(f_):
        x_index = 0
        index=0
        for i in [1024, 1024],[1117, 1024],[1117, 1024],[1024, 1024]:
            index+=1
            c_image = image.crop((x_index,0,x_index+i[0],i[1]))
            x_index+=i[0]
            c_image.save(out_folder/(str(index)+f_.name))

    elif "L2_g0_2345" in str(f_):
        x_index = 0
        index=0
        for i in [1303, 1024],[1117, 1024],[1117, 1024],[1024, 1024]:
            index+=1
            c_image = image.crop((x_index,0,x_index+i[0],i[1]))
            x_index+=i[0]
            c_image.save(out_folder/(str(index)+f_.name))
    else:
        x_index = 0
        index=0
        iw = int(w/4)
        for i in [iw, h],[iw, h],[iw, h],[iw, h]:
            index+=1
            c_image = image.crop((x_index,0,x_index+i[0],i[1]))
            x_index+=i[0]
            c_image.save(out_folder/(str(index)+f_.name))