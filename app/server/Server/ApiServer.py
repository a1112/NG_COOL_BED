import logging
from threading import Thread

import uvicorn
from Configs import ServerConfig
from Server.Base import app


def _thread_server_start_():
    logging.info("start server")

    uvicorn.run(
        app,
        host=ServerConfig.server_ip,
        port=ServerConfig.server_port,
        log_level="info",
        access_log=True,
    )

def start():
    Thread(target=_thread_server_start_).start()
