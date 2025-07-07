import socket
from pathlib import Path


class DebugFolderConfig:
    if socket.gethostname() == 'DESKTOP-94ADH1G':
        # For coolbed
        DATA_FOLDER = Path(r'/home/coolbed/steelSeg/datas')
        MODEL_FOLDER = Path(r'/home/coolbed/steelSeg/models')


if __name__ == "__main__":
    print(socket.gethostname())
    print(DebugFolderConfig.DATA_FOLDER)
    print(DebugFolderConfig.MODEL_FOLDER)