import io

from PIL import Image, ImageFont
from PIL import ImageDraw

# 创建带有白色背景的图像
width, height = 150, 150
image = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(image)

# 加载字体
font = ImageFont.load_default(30)

# 要添加的文本
text = "Not Found"

bbox = draw.textbbox((0, 0), text, font=font)
text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
position = ((width - text_width) / 2, (height - text_height) / 2)
# 在图像上添加文本
draw.text(position, text, fill="black", font=font)
img_byte_arr = io.BytesIO()
image.save(img_byte_arr, format='jpeg')
img_byte_arr.seek(0)
noFindImageByte = img_byte_arr.getvalue()