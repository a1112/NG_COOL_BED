import os
from pathlib import Path

import shutil

from PIL import Image


files = Path(fr"G:\LG\NG_COOL_BED\config\camera\calibrate\calibrate_1")


for f_ in files.glob("*.bmp"):
    image = Image.open(f_)
    image.save(f_.with_suffix(".jpg"))
    image.close()
    os.remove(f_)