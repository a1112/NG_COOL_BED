from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from Result.DetResult import DetResult
    from Configs.GroupConfig import GroupConfig


PRIORITY_SHARES = {
    1: 0.40,
    2: 0.40,
    3: 0.20,
}

PRIORITY_LABELS = {
    1: "发送中/有钢板",
    2: "有数据未发送",
    3: "等待图像",
    4: "已屏蔽",
}


@dataclass
class GroupPriorityState:
    cool_bed_key: str
    group_key: str
    shielded: bool = False
    is_sending: bool = False
    has_data: bool = False
    has_steel: bool = False
    last_detection_time: float = 0.0
    last_send_time: float = 0.0
    last_result: Optional["DetResult"] = None
    level: int = 3
    reason: str = PRIORITY_LABELS[3]

    def to_dict(self) -> Dict[str, object]:
        return {
            "group_key": self.group_key,
            "priority_level": self.level,
            "priority_reason": self.reason,
            "shielded": self.shielded,
            "is_sending": self.is_sending,
            "has_data": self.has_data,
            "has_steel": self.has_steel,
            "last_detection_time": self.last_detection_time,
            "last_send_time": self.last_send_time,
        }


class CoolBedPriorityController:
    def __init__(self, cool_bed_key: str):
        self.cool_bed_key = cool_bed_key
        self._states: Dict[str, GroupPriorityState] = {}
        self._lock = threading.RLock()
        self._round_robin: Dict[int, int] = {1: 0, 2: 0, 3: 0}

    def initialize_groups(self, groups: Iterable["GroupConfig"]):
        with self._lock:
            for group in groups:
                shield_flag = getattr(group, "shield", False)
                self._states[group.group_key] = GroupPriorityState(
                    cool_bed_key=self.cool_bed_key,
                    group_key=group.group_key,
                    shielded=shield_flag,
                )

    def update_shield(self, group_key: str, shield: bool):
        with self._lock:
            state = self._states.get(group_key)
            if not state:
                return
            state.shielded = bool(shield)
            if state.shielded:
                state.is_sending = False
            self._update_level(state)

    def record_detection(self, group_key: str, result: Optional["DetResult"]):
        with self._lock:
            state = self._states.get(group_key)
            if not state:
                return
            state.last_result = result
            state.last_detection_time = time.time()
            if result is None:
                state.has_data = False
                state.has_steel = False
            else:
                state.has_data = bool(result.can_get_data)
                state.has_steel = bool(getattr(result, "steel_list", []))
            self._update_level(state)

    def mark_sending(self, group_key: Optional[str]):
        with self._lock:
            now = time.time()
            for state in self._states.values():
                if group_key is None:
                    state.is_sending = False
                else:
                    is_current = state.group_key == group_key
                    state.is_sending = is_current
                    if is_current:
                        state.last_send_time = now
                self._update_level(state)

    def _active_states(self) -> List[GroupPriorityState]:
        return [
            state
            for state in self._states.values()
            if not state.shielded
        ]

    def _update_level(self, state: GroupPriorityState):
        if state.shielded:
            state.level = 4
            state.reason = PRIORITY_LABELS[4]
            return
        if state.is_sending and state.has_steel:
            state.level = 1
        elif state.has_data:
            state.level = 2
        else:
            state.level = 3
        state.reason = PRIORITY_LABELS.get(state.level, PRIORITY_LABELS[3])

    def _need_bootstrap(self) -> List[str]:
        pending = [
            state.group_key
            for state in self._active_states()
            if state.last_result is None
        ]
        return pending

    def next_iteration_groups(self) -> List[str]:
        with self._lock:
            active_states = self._active_states()
            if not active_states:
                return []
            pending = self._need_bootstrap()
            if pending:
                return pending

            level_buckets: Dict[int, List[GroupPriorityState]] = {1: [], 2: [], 3: []}
            for state in active_states:
                self._update_level(state)
                bucket = min(state.level, 3)
                level_buckets[bucket].append(state)
            for bucket in level_buckets.values():
                bucket.sort(key=lambda item: item.group_key)

            total_ops = len(active_states)
            ops_by_level = self._distribute_ops(level_buckets, total_ops)
            selected: List[str] = []
            for level in (1, 2, 3):
                bucket = level_buckets[level]
                if not bucket:
                    continue
                count = ops_by_level.get(level, 0)
                if count <= 0:
                    continue
                idx = self._round_robin[level] % len(bucket)
                for _ in range(count):
                    state = bucket[idx % len(bucket)]
                    selected.append(state.group_key)
                    idx += 1
                self._round_robin[level] = idx % len(bucket)
            return selected

    def _distribute_ops(
        self,
        level_buckets: Dict[int, List[GroupPriorityState]],
        total_ops: int,
    ) -> Dict[int, int]:
        if total_ops <= 0:
            return {1: 0, 2: 0, 3: 0}
        ops_by_level = {1: 0, 2: 0, 3: 0}
        remaining = total_ops
        for level in (1, 2, 3):
            bucket_size = len(level_buckets[level])
            if bucket_size == 0:
                ops_by_level[level] = 0
                continue
            desired = int(round(total_ops * PRIORITY_SHARES[level]))
            desired = min(desired, bucket_size)
            if desired == 0:
                desired = 1
            ops_by_level[level] = desired
            remaining -= desired
        if remaining < 0:
            for level in (3, 2, 1):
                reducible = min(ops_by_level[level], -remaining)
                ops_by_level[level] -= reducible
                remaining += reducible
                if remaining >= 0:
                    break
        elif remaining > 0:
            for level in (1, 2, 3):
                bucket_size = len(level_buckets[level])
                if bucket_size == 0:
                    continue
                available = bucket_size - ops_by_level[level]
                if available <= 0:
                    continue
                add = min(available, remaining)
                ops_by_level[level] += add
                remaining -= add
                if remaining == 0:
                    break
        return ops_by_level

    def cached_result(self, group_key: str) -> Optional["DetResult"]:
        with self._lock:
            state = self._states.get(group_key)
            return state.last_result if state else None

    def dump_states(self) -> Dict[str, Dict[str, object]]:
        with self._lock:
            return {key: state.to_dict() for key, state in self._states.items()}

    def state_for(self, group_key: str) -> Optional[GroupPriorityState]:
        with self._lock:
            return self._states.get(group_key)


class PriorityRegistry:
    def __init__(self):
        self._controllers: Dict[str, CoolBedPriorityController] = {}
        self._lock = threading.RLock()

    def create_controller(
        self,
        cool_bed_key: str,
        groups: Iterable["GroupConfig"],
    ) -> CoolBedPriorityController:
        controller = CoolBedPriorityController(cool_bed_key)
        controller.initialize_groups(groups)
        with self._lock:
            self._controllers[cool_bed_key] = controller
        return controller

    def get_controller(self, cool_bed_key: str) -> Optional[CoolBedPriorityController]:
        with self._lock:
            return self._controllers.get(cool_bed_key)

    def mark_sending(self, cool_bed_key: str, group_key: Optional[str]):
        controller = self.get_controller(cool_bed_key)
        if controller:
            controller.mark_sending(group_key)

    def record_detection(
        self,
        cool_bed_key: str,
        group_key: str,
        result: Optional["DetResult"],
    ):
        controller = self.get_controller(cool_bed_key)
        if controller:
            controller.record_detection(group_key, result)

    def update_shield(self, cool_bed_key: str, group_key: str, shield: bool):
        controller = self.get_controller(cool_bed_key)
        if controller:
            controller.update_shield(group_key, shield)

    def dump(self) -> Dict[str, Dict[str, Dict[str, object]]]:
        with self._lock:
            return {
                cool_bed: controller.dump_states()
                for cool_bed, controller in self._controllers.items()
            }


priority_registry = PriorityRegistry()
