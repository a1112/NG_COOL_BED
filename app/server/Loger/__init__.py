import logging
from logging.handlers import TimedRotatingFileHandler
import os
import string
import multiprocessing
from pathlib import Path
import colorlog

import CONFIG

# 创建控制台和文件处理器
# 获取日志记录器
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 清除现有的处理器，防止重复添加
if logger.hasHandlers():
    logger.handlers.clear()

# 创建一个替换标点符号的表，用于进程名称
translator = str.maketrans(string.punctuation, "_" * len(string.punctuation))

# ??????????????????
log_dir = Path(__file__).resolve().parents[2] / "logs" / "server"
log_dir.mkdir(parents=True, exist_ok=True)

# ??????????????????????????????????????????????????????
proc_name = multiprocessing.current_process().name.translate(translator)
filename = os.path.join(log_dir, f"{proc_name}.log")

# ?????????????????????????????????????????????
file_handler = TimedRotatingFileHandler(
    filename,
    when="midnight",
    interval=1,
    backupCount=1000,
    encoding="utf-8",
)
file_handler.suffix = "%Y-%m-%d"

# ????????????????????????
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 使用彩色日志格式输出到控制台
console_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

