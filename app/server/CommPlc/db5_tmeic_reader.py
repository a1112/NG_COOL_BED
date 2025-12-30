import datetime
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, Any

from HslCommunication import SiemensS7Net, SiemensPLCS
from snap7.util import get_bool, get_int, get_real, get_string

import PLC_config
from CONFIG import DEBUG_MODEL
from Loger import logger


def _read_real(chunk: bytes) -> float:
    return float(get_real(chunk, 0))


def _read_int(chunk: bytes) -> int:
    return int(get_int(chunk, 0))


def _read_string(chunk: bytes) -> str:
    return get_string(chunk, 0).strip()


def _read_bool(payload: bytes, byte_index: int, bit_index: int) -> bool:
    try:
        return bool(get_bool(payload, byte_index, bit_index))
    except Exception:
        return False


@dataclass(frozen=True)
class SliceField:
    name: str
    start: int
    end: int
    parser: Callable[[bytes], Any]

    def decode(self, payload: bytes) -> Any:
        return self.parser(payload[self.start:self.end])




class Db5TmeicReader(threading.Thread):
    """读取 TMEIC -> 识别 的 DB5 数据。"""

    def __init__(
        self,
        db_address: str | None = None,
        db_length: int | None = None,
        poll_interval: float = 0.05,
    ) -> None:
        super().__init__(daemon=True)
        self._running = True
        self._poll_interval = poll_interval
        self._db_address = db_address or PLC_config.TMEIC_DB5_ADDRESS
        self._db_length = db_length or PLC_config.TMEIC_DB5_LENGTH
        self._latest: Dict[str, Any] = {}
        self._plc_ip = PLC_config.IP_L1
        self._rack = PLC_config.ROCK
        self._slot = PLC_config.SLOT

        self._client = SiemensS7Net(SiemensPLCS.S400, self._plc_ip)
        self._client.SetSlotAndRack(self._rack, self._slot)
        self.start()

    def close(self) -> None:
        self._running = False

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._latest)

    def run(self) -> None:
        while self._running:
            time.sleep(self._poll_interval)
            start = time.time()
            try:
                response = self._client.Read(self._db_address, self._db_length)
                raw = response.Content
                timestamp = datetime.datetime.now()
            except Exception as exc:  # pragma: no cover - hardware dependent
                logger.error(
                    "DB5 read error ip=%s rack=%s slot=%s db=%s len=%s err=%s",
                    self._plc_ip,
                    self._rack,
                    self._slot,
                    self._db_address,
                    self._db_length,
                    exc,
                )
                continue
            try:
                decoded = self._decode(raw)
                decoded["getDateTime"] = timestamp
                decoded["getTimeLen"] = time.time() - start
                self._latest = decoded
            except Exception as exc:  # pragma: no cover - decoding guard
                logger.error(
                    "DB5 decode error ip=%s rack=%s slot=%s db=%s len=%s err=%s",
                    self._plc_ip,
                    self._rack,
                    self._slot,
                    self._db_address,
                    self._db_length,
                    exc,
                )

    @staticmethod
    def _decode(payload: bytes) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        # result.update(_decode_bool_flags(payload[2:4]))
        result["O_NAI_W1_spare5"] = _read_bool(payload, 3, 4)
        result["O_NAI_W1_spare6"] = _read_bool(payload, 3, 5)
        # for field in DB5_FIELD_SPECS:
        #     result[field.name] = field.decode(payload)
        return result


class Db5TmeicReaderDebug(threading.Thread):
    """仿真 DB5 读取：DEBUG_MODEL 下避免真实 PLC 依赖。"""

    def __init__(self, interval: float = 0.25) -> None:
        super().__init__(daemon=True)
        self._interval = interval
        self._running = True
        self._tick = 0
        self._latest: Dict[str, Any] = {}
        self.start()

    def close(self) -> None:
        self._running = False

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._latest)

    def run(self) -> None:
        while self._running:
            time.sleep(self._interval)
            self._tick += 1
            payload: Dict[str, Any] = {
                "getDateTime": datetime.datetime.now(),
                "getTimeLen": self._interval,
            }
            payload["STEEL_NO"] = f"SIM-{self._tick:04d}"
            self._latest = payload
            time.sleep(5)

def create_db5_reader() -> Db5TmeicReader | Db5TmeicReaderDebug:
    return Db5TmeicReaderDebug() if DEBUG_MODEL else Db5TmeicReader()


__all__ = [
    "Db5TmeicReader",
    "Db5TmeicReaderDebug",
    "create_db5_reader",
]
