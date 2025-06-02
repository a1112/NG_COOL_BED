#  seg 模式

from labelme2yolov8.l2y import Labelme2YOLOv8


Labelme2YOLOv8(
    fr'G:\LG\NG_COOL_BED_DATA\0527\0527',
    "polygon",
    ["steel"]
).convert(0,0)