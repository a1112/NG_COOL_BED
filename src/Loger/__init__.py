import logging
logger = logging.getLogger("../log")
logger.setLevel(logging.DEBUG)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_formatter = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# 文件处理器（详细日志）
file_handler = logging.FileHandler("debug.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)