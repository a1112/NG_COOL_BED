import threading
import time

from HslCommunication import SiemensPLCS, SiemensS7Net

import PLC_config
from CONFIG import DEBUG_MODEL
from Loger import logger


def decode_db6_packet(data: bytes) -> dict | None:
    if len(data) < 64:
        return None

    buf = memoryview(data)

    def read_int16(offset: int) -> int:
        return int.from_bytes(buf[offset:offset + 2], "little", signed=True)

    def read_bools(byte_val: int) -> list[bool]:
        return [bool((byte_val >> (7 - i)) & 0x01) for i in range(8)]

    alive_cnt = read_int16(0)
    bools_1 = read_bools(int(buf[2]))
    bools_2 = read_bools(int(buf[3]))

    decoded: dict = {
        "I_NAI_W0_ALV_CNT": alive_cnt,
        "I_NAI_MET_F1": bools_1[0],
        "I_NAI_MET_F2": bools_1[1],
        "I_NAI_MET_F5": bools_1[2],
        "I_NAI_MET_F6": bools_1[3],
        "I_NAI_LONG_CB1": bools_1[4],
        "I_NAI_LONG_CB2": bools_1[5],
        "I_NAI_ERROR_CB1": bools_1[6],
        "I_NAI_ERROR_CB2": bools_1[7],
        "I_NAI_LONG_F12": bools_2[0],
        "I_NAI_LONG_F56": bools_2[1],
        "I_NAI_W1_spare1": bools_2[2],
        "I_NAI_W1_spare2": bools_2[3],
        "I_NAI_W1_spare3": bools_2[4],
        "I_NAI_W1_spare4": bools_2[5],
        "I_NAI_W1_spare5": bools_2[6],
        "I_NAI_W1_spare6": bools_2[7],
    }

    int_keys = [
        "I_NAI_X_dis_CB1G3",
        "I_NAI_Y_dis_CB1G3",
        "I_NAI_Len_CB1G3",
        "I_NAI_Wid_CB1G3",
        "I_NAI_Ang_CB1G3",
        "I_NAI_X_dis_CB1G4",
        "I_NAI_Y_dis_CB1G4",
        "I_NAI_Len_CB1G4",
        "I_NAI_Wid_CB1G4",
        "I_NAI_Ang_CB1G4",
        "I_NAI_X_dis_CB2G3",
        "I_NAI_Y_dis_CB2G3",
        "I_NAI_Len_CB2G3",
        "I_NAI_Wid_CB2G3",
        "I_NAI_Ang_CB2G3",
        "I_NAI_X_dis_CB2G4",
        "I_NAI_Y_dis_CB2G4",
        "I_NAI_Len_CB2G4",
        "I_NAI_Wid_CB2G4",
        "I_NAI_Ang_CB2G4",
        "I_NAI_Y_dis_F1",
        "I_NAI_Ang_F1",
        "I_NAI_Y_dis_F2",
        "I_NAI_Ang_F2",
        "I_NAI_Y_dis_F5",
        "I_NAI_Ang_F5",
        "I_NAI_Y_dis_F6",
        "I_NAI_Ang_F6",
        "I_NAI_W30_spare",
        "I_NAI_W31_spare",
    ]
    offset = 4
    for key in int_keys:
        decoded[key] = read_int16(offset)
        offset += 2

    return decoded


class Db6RecognitionSender(threading.Thread):
    """DB6：识别 -> TMEIC，负责写入 PLC。"""

    def __init__(self, poll_interval: float = 0.1) -> None:
        super().__init__(daemon=True)
        self._poll_interval = poll_interval
        self._running = True
        self._db_address = "DB6.0"
        self._db_length = 64
        self._client = SiemensS7Net(SiemensPLCS.S400, PLC_config.IP_L1)
        self._client.SetSlotAndRack(PLC_config.ROCK, PLC_config.SLOT)
        self.last_data_dict = {}
        self.last_bytes: bytes = b""
        self._last_read_error_ts = 0.0
        self.start()

    def close(self) -> None:
        self._running = False

    def run(self) -> None:
        while self._running:
            time.sleep(self._poll_interval)
            try:
                start_time = time.time()
                response = self._client.Read(self._db_address, self._db_length)
                if response is None:
                    raise RuntimeError("DB6 read: response is None")
                if hasattr(response, "IsSuccess") and not response.IsSuccess:
                    msg = getattr(response, "Message", "") or ""
                    raise RuntimeError(f"DB6 read failed: {msg}".strip())

                payload = getattr(response, "Content", None)
                if payload is None:
                    raise RuntimeError("DB6 read: Content is None")

                if isinstance(payload, (bytes, bytearray, memoryview)):
                    payload_bytes = bytes(payload)
                else:
                    payload_bytes = bytes(payload)

                self.last_bytes = payload_bytes
                self._decode(payload_bytes, {
                    "getDateTime": time.time(),
                    "getTimeLen": time.time() - start_time,
                })
            except Exception as exc:  # pragma: no cover - 真实 PLC
                now = time.time()
                if now - self._last_read_error_ts >= 2.0:
                    self._last_read_error_ts = now
                    logger.error("DB6 read error: %s", exc)

    def _decode(self, data: bytes, other: dict) -> None:
        decoded = decode_db6_packet(data)
        if decoded is None:
            return
        self.last_data_dict.update({**decoded, **other})

    def write_bytes(self, packet: bytes) -> None:
        self._client.Write(self._db_address, bytearray(packet))

    def write_byte(self, packet: bytes) -> None:
        self.write_bytes(packet)


class Db6RecognitionDebug:
    def __init__(self) -> None:
        self.last_data_dict = {}
        self.last_bytes: bytes = b""

    def write_bytes(self, packet: bytes) -> None:  # pragma: no cover - 仿真
        self.last_bytes = bytes(packet)
        decoded = decode_db6_packet(self.last_bytes)
        if decoded is not None:
            self.last_data_dict.update({**decoded, "getDateTime": time.time(), "getTimeLen": 0.0})
        logger.debug("DB6 mock write len: %s", len(packet))

    def write_byte(self, packet: bytes) -> None:  # pragma: no cover - mock
        self.write_bytes(packet)

    def select(self, select_list: list[int] | None = None) -> bool:  # pragma: no cover
        logger.debug("DB6 mock select %s", select_list)
        return True


def create_db6_sender() -> Db6RecognitionSender | Db6RecognitionDebug:
    return Db6RecognitionDebug() if DEBUG_MODEL else Db6RecognitionSender()


db6_sender = create_db6_sender()


if __name__ == "__main__":  # pragma: no cover
    logger.debug("__main__")
