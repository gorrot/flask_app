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


