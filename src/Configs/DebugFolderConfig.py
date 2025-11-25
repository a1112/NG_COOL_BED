import socket
from pathlib import Path


class DebugFolderConfig:
    if socket.gethostname() == 'DESKTOP-3VCH6DO':
        # For coolbed
        DATA_FOLDER = Path(r'P:\data_tool\PreData\ng\seg0611')
    if socket.gethostname() == 'lcx_ace':
        DATA_FOLDER = Path(r'K:\data_tool\PreData\ng\seg0611')
    FOLDER_L1_g0_2345 = DATA_FOLDER / "L1_g0_2345"
    FOLDER_L1_g1_6 = DATA_FOLDER / "L1_g1_6"
    FOLDER_L1_g2_1 = DATA_FOLDER / "L1_g2_1"

    FOLDER_L2_g0_2345 = DATA_FOLDER / "L2_g0_2345"
    FOLDER_L2_g1_6 = DATA_FOLDER / "L2_g1_6"
    FOLDER_L2_g2_1 = DATA_FOLDER / "L2_g2_1"
    FOLDER_L2_g2_7 = DATA_FOLDER / "L2_g2_7"
    FOLDER_MAP = {
        "L1_g0_2345": FOLDER_L1_g0_2345,
        "L1_g1_6": FOLDER_L1_g1_6,
        "L1_g2_1": FOLDER_L1_g2_1,
        "L2_g0_2345": FOLDER_L2_g0_2345,
        "L2_g1_6": FOLDER_L2_g1_6,
        "L2_g2_1": FOLDER_L2_g2_1,
        "L2_g2_7": FOLDER_L2_g2_7,
    }

if __name__ == "__main__":
    print(socket.gethostname())
    print(DebugFolderConfig.DATA_FOLDER.exists())
