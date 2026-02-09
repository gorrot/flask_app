from typing import List
import threading
from domain.entities import Detection
from domain.value_objects import DetectionStatus


class InMemoryDetectionRepository:
    """内存中的检测数据仓库"""
    
    def __init__(self, max_history: int = 1000):
        self._data: List[Detection] = []
        self._lock = threading.Lock()
        self._max_history = max_history
    
    def add(self, detection: Detection) -> Detection:
        """添加检测数据"""
        with self._lock:
            self._data.append(detection)
            # 保持数据量在合理范围内
            if len(self._data) > self._max_history:
                self._data.pop(0)
        return detection
    
    def get_unread(self, limit: int = 50) -> List[Detection]:
        """获取未读数据"""
        with self._lock:
            unread_data = [
                d for d in self._data 
                if d.status == DetectionStatus.UNREAD
            ]
            return unread_data[-limit:] if unread_data else []
    
    def get_all(self, limit: int = 50) -> List[Detection]:
        """获取所有数据"""
        with self._lock:
            return self._data[-limit:] if self._data else []

    def get_by_types(self, types: List[str], limit: int = 50) -> List[Detection]:
        """按类型筛选，返回指定类型的最新 limit 条（用于三期等按类型拉取）"""
        with self._lock:
            if not types:
                return self._data[-limit:] if self._data else []
            type_set = set(types)
            filtered = [d for d in self._data if d.detection_type.value in type_set]
            return filtered[-limit:] if filtered else []

    def get_by_types_balanced(self, types: List[str], limit: int = 50) -> List[Detection]:
        """多类型固定配额，且每类型至少 1 条（若有）：先保证每类最新 1 条，再按时间填满 limit。
        避免 load_monitor、phase3_mill_change 等低频类型被完全挤出。"""
        with self._lock:
            if not types:
                return self._data[-limit:] if self._data else []
            type_list = list(dict.fromkeys(types))
            n = len(type_list)
            quota = max(1, (limit + n - 1) // n)
            by_type: dict = {t: [] for t in type_list}
            for d in self._data:
                t = d.detection_type.value
                if t not in by_type:
                    continue
                by_type[t].append(d)
            # 1）每类型至少 1 条（取该类型最新一条）
            guaranteed = []
            for t in type_list:
                if by_type[t]:
                    guaranteed.append(by_type[t][-1])
            guaranteed_ids = {d.id for d in guaranteed}
            # 2）每类型最多 quota 条，去掉已选的 1 条，其余加入候选池，按 id 降序
            rest = []
            for t in type_list:
                lst = by_type[t][-quota:]
                rest.extend([d for d in lst if d.id not in guaranteed_ids])
            rest.sort(key=lambda d: d.id, reverse=True)
            # 3）结果 = 每类至少 1 条 + 按时间填满至 limit
            result = guaranteed + rest[: max(0, limit - len(guaranteed))]
            result.sort(key=lambda d: d.id, reverse=True)
            return result[:limit]
    
    def mark_as_read(self, detection_id: int) -> bool:
        """标记数据为已读"""
        with self._lock:
            for detection in self._data:
                if detection.id == detection_id:
                    detection.mark_as_read()
                    return True
            return False
    
    def get_all_detections(self) -> List[Detection]:
        """获取所有检测数据（用于统计）"""
        with self._lock:
            return self._data.copy()
    
    def count_total(self) -> int:
        """获取总数"""
        with self._lock:
            return len(self._data)
    
    def count_unread(self) -> int:
        """获取未读数"""
        with self._lock:
            return len([
                d for d in self._data 
                if d.status == DetectionStatus.UNREAD
            ])

    def count_by_types(self, types: List[str]) -> dict:
        """按类型统计数量，用于召回检查。返回 { type_value: count }"""
        with self._lock:
            type_set = set(types)
            counts = {}
            for d in self._data:
                t = d.detection_type.value
                if t in type_set:
                    counts[t] = counts.get(t, 0) + 1
            return counts



