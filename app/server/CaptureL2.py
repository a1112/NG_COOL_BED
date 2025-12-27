import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import CONFIG
from CaptureService import CaptureService
from Configs.CaptureServerConfig import CAPTURE_BIND_HOST, CAPTURE_PORTS


def main():
    CONFIG.SHOW_OPENCV = True
    CONFIG.SHOW_STEEL_PREDICT = True
    service = CaptureService("L2")
    service.run(CAPTURE_BIND_HOST, CAPTURE_PORTS["L2"])


if __name__ == "__main__":
    main()
