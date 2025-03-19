import logging
from threading import Thread

import uvicorn

from Configs import ServerConfig

def _thread_server_start_():
    logging.info("start server")
    from Server.Base import app
    uvicorn.run(app, host=ServerConfig.server_ip, port=ServerConfig.server_port)

def start():
    Thread(target=_thread_server_start_).start()