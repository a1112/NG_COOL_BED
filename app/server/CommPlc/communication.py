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

    def __init__(self, poll_interval: float = 2) -> None:
        super().__init__(daemon=True)
        self._poll_interval = poll_interval
        self._running = True
        self._db_address = "DB6.0"
        self._db_length = 64
        self._plc_ip = PLC_config.IP_L1
        self._rack = PLC_config.ROCK
        self._slot = PLC_config.SLOT
        self._client = SiemensS7Net(SiemensPLCS.S400, self._plc_ip)
        self._client.SetSlotAndRack(self._rack, self._slot)
        self.last_data_dict = {}
        self.last_bytes: bytes = b""
        self.last_write_ok_ts: float | None = None
        self.last_write_error: str = ""
        self._min_write_interval_s = 0.3
        self._last_write_ts = 0.0
        self._last_read_ts = 0.0
        self._last_write_error_ts = 0.0
        self._last_read_error_ts = 0.0
        self._write_lock = threading.Lock()
        self._pending_packet: bytes | None = None
        self._write_fail_count = 0
        self._last_reconnect_ts = 0.0
        self.start()

    def close(self) -> None:
        self._running = False

    def run(self) -> None:
        while self._running:
            now = time.time()
            if now - self._last_read_ts >= self._poll_interval:
                self._last_read_ts = now
                try:
                    start_time = time.time()
                    response = self._client.Read(self._db_address, self._db_length)
                    if response is None:
                        raise RuntimeError("DB6 read: response is None")
                    # if hasattr(response, "IsSuccess") and not response.IsSuccess:
                    #     msg = getattr(response, "Message", "") or ""
                    #     raise RuntimeError(f"DB6 read failed: {msg}".strip())

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
                        logger.error(
                            "DB6 read error ip=%s rack=%s slot=%s db=%s len=%s err=%s",
                            self._plc_ip,
                            self._rack,
                            self._slot,
                            self._db_address,
                            self._db_length,
                            exc,
                        )

            if (now - self._last_write_ts) >= self._min_write_interval_s:
                packet = None
                with self._write_lock:
                    if self._pending_packet is not None:
                        packet = self._pending_packet
                        self._pending_packet = None
                if packet is not None:
                    self._do_write(packet)

            time.sleep(0.02)

    def _decode(self, data: bytes, other: dict) -> None:
        decoded = decode_db6_packet(data)
        if decoded is None:
            return
        self.last_data_dict.update({**decoded, **other})

    def _do_write(self, packet: bytes) -> None:
        try:
            now = time.time()
            self._last_write_ts = now
            response = self._client.Write(self._db_address, bytearray(packet))

            ok = True
            message = ""
            if response is None:
                ok = False
                message = "DB6 write: response is None"
            elif hasattr(response, "IsSuccess"):
                ok = bool(getattr(response, "IsSuccess", False))
                message = getattr(response, "Message", "") or ""
            elif isinstance(response, bool):
                ok = response

            if ok:
                self.last_write_ok_ts = time.time()
                self.last_write_error = ""
                self._write_fail_count = 0
                return

            self._write_fail_count += 1
            self.last_write_error = (
                f"DB6 write failed ip={self._plc_ip} rack={self._rack} slot={self._slot} "
                f"db={self._db_address} len={self._db_length} msg={message or ''}"
            ).strip()
            if now - self._last_write_error_ts >= 2.0:
                self._last_write_error_ts = now
                logger.error("%s", self.last_write_error)
            if self._write_fail_count >= 5:
                self._reconnect_if_needed(now, reason="write failed")
        except Exception as exc:  # pragma: no cover - runtime only
            now = time.time()
            self._write_fail_count += 1
            self.last_write_error = (
                f"DB6 write error ip={self._plc_ip} rack={self._rack} slot={self._slot} "
                f"db={self._db_address} len={self._db_length} err={exc}"
            )
            if now - self._last_write_error_ts >= 2.0:
                self._last_write_error_ts = now
                logger.error("%s", self.last_write_error)
            if self._write_fail_count >= 5:
                self._reconnect_if_needed(now, reason="write exception")

    def _reconnect_if_needed(self, now: float, reason: str) -> None:
        if now - self._last_reconnect_ts < 5.0:
            return
        self._last_reconnect_ts = now
        self._write_fail_count = 0
        try:
            logger.warning(
                "DB6 reconnecting ip=%s rack=%s slot=%s reason=%s",
                self._plc_ip,
                self._rack,
                self._slot,
                reason,
            )
            if hasattr(self._client, "ConnectClose"):
                try:
                    self._client.ConnectClose()
                except Exception:
                    pass
            if hasattr(self._client, "ConnectServer"):
                self._client.ConnectServer()
        except Exception as exc:
            logger.error(
                "DB6 reconnect failed ip=%s rack=%s slot=%s err=%s",
                self._plc_ip,
                self._rack,
                self._slot,
                exc,
            )

    def write_byte(self, packet: bytes) -> None:
        self.write_bytes(packet)

    def write_bytes(self, packet: bytes) -> None:
        if packet is None:
            return
        with self._write_lock:
            self._pending_packet = bytes(packet)


class Db6RecognitionDebug:
    def __init__(self) -> None:
        self.last_data_dict = {}
        self.last_bytes: bytes = b""
        self.last_write_ok_ts: float | None = None
        self.last_write_error: str = ""
        self._last_write_ts = 0.0

    def write_bytes(self, packet: bytes) -> None:  # pragma: no cover - 仿真
        now = time.time()
        if hasattr(self, "_last_write_ts") and (now - self._last_write_ts) < 0.3:
            return
        self._last_write_ts = now
        self.last_bytes = bytes(packet)
        self.last_write_ok_ts = time.time()
        self.last_write_error = ""
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
