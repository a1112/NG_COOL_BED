import logging
from typing import Dict, Optional

import numpy as np
import requests

from Configs.CalibrateConfig import CalibrateConfig
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Result.DetResult import DetResult


class CaptureHttpClient:
    def __init__(self, cool_bed_key: str, base_url: str, timeout: float = 0.8):
        self.cool_bed_key = cool_bed_key
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self._last_payload = None
        self._dummy_image_cache = {}
        self._logger = logging.getLogger("root")

    def _build_dummy_image(self, width: int, height: int):
        key = (int(width), int(height))
        cached = self._dummy_image_cache.get(key)
        if cached is not None:
            return cached
        image = np.zeros((int(height), int(width), 3), dtype=np.uint8)
        self._dummy_image_cache[key] = image
        return image

    def _build_det_result(self, group_config, rec_list):
        map_config = group_config.map_config
        dummy_image = self._build_dummy_image(map_config.width, map_config.height)
        calibrate = CalibrateConfig([dummy_image])
        return DetResult(calibrate, rec_list or [], map_config)

    def fetch_payload(self) -> Optional[dict]:
        if not self.base_url:
            return None
        try:
            resp = self.session.get(f"{self.base_url}/boxes", timeout=self.timeout)
            resp.raise_for_status()
            payload = resp.json()
            self._last_payload = payload
            return payload
        except Exception:
            self._logger.exception(
                "capture fetch failed url=%s timeout=%s",
                f"{self.base_url}/boxes",
                self.timeout,
            )
            return self._last_payload

    def get_steel_info(self, config: CoolBedGroupConfig) -> Optional[Dict[str, DetResult]]:
        payload = self.fetch_payload()
        if not isinstance(payload, dict):
            return None
        groups_payload = payload.get("groups")
        if not isinstance(groups_payload, dict):
            return None
        result = {}
        for group_config in config.groups:
            group_key = group_config.group_key
            group_payload = groups_payload.get(group_key)
            if not isinstance(group_payload, dict):
                result[group_key] = None
                continue
            rec_list = group_payload.get("rec_list")
            if rec_list is None:
                result[group_key] = None
                continue
            result[group_key] = self._build_det_result(group_config, rec_list)
        return result


def payload_timestamp(payload: Optional[dict]) -> float:
    if isinstance(payload, dict):
        try:
            return float(payload.get("timestamp") or 0.0)
        except Exception:
            return 0.0
    return 0.0
