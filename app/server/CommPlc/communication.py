import datetime
import threading
import time

from HslCommunication import SiemensPLCS, SiemensS7Net
from snap7.util import get_real

import PLC_config
from CONFIG import DEBUG_MODEL
from Loger import logger


class Db6RecognitionSender(threading.Thread):
    """DB6：识别 -> TMEIC，负责写入 PLC。"""

    def __init__(self, poll_interval: float = 0.01) -> None:
        super().__init__(daemon=True)
        self._poll_interval = poll_interval
        self._running = True
        self._db_address = "DB6.0"
        self._db_length = 64
        self._client = SiemensS7Net(SiemensPLCS.S400, PLC_config.IP_L1)
        self._client.SetSlotAndRack(PLC_config.ROCK, PLC_config.SLOT)
        self.last_data_dict = {}
        self.max_temp = 0.0
        self.old_temp_in = 0.0
        self.start()

    def close(self) -> None:
        self._running = False

    def run(self) -> None:
        while self._running:
            time.sleep(self._poll_interval)
            try:
                start_time = time.time()
                response = self._client.Read(self._db_address, self._db_length)
                payload = response.Content
                timestamp = datetime.datetime.now()
                self._decode(payload, {
                    "getDateTime": timestamp,
                    "getTimeLen": time.time() - start_time,
                })
            except Exception as exc:  # pragma: no cover - 真实 PLC
                logger.error("DB6 read error: %s", exc)

    def _decode(self, data: bytes, other: dict) -> None:
        steel = data[34:54].strip(b"\x00").decode(errors="ignore")
        temp_in = get_real(data[22:26], 0)
        self.old_temp_in = max(self.old_temp_in, temp_in)
        self.max_temp = self.old_temp_in
        self.last_data_dict.update({
            "steel_no": steel,
            "temp_in": temp_in,
            **other,
        })

    def select(self, select_list: list[int] | None = None) -> bool:
        select_list = select_list or [0] * 8
        plc_list = ["0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "1.0", "1.1"]
        for address, flag in zip(plc_list, select_list):
            self._client.WriteBool(f"DB4600.{address}", bool(flag))
        return True

    def write_bytes(self, packet: bytes) -> None:
        self._client.Write(self._db_address, bytearray(packet))


class Db6RecognitionDebug:
    def write_bytes(self, packet: bytes) -> None:  # pragma: no cover - 仿真
        logger.debug("DB6 mock write len: %s", len(packet))

    def select(self, select_list: list[int] | None = None) -> bool:  # pragma: no cover
        logger.debug("DB6 mock select %s", select_list)
        return True


def create_db6_sender() -> Db6RecognitionSender | Db6RecognitionDebug:
    return Db6RecognitionDebug() if DEBUG_MODEL else Db6RecognitionSender()


db6_sender = create_db6_sender()


if __name__ == "__main__":  # pragma: no cover
    logger.debug("__main__")
