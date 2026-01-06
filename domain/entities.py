from dataclasses import dataclass
from typing import Optional
from domain.value_objects import DetectionType, DetectionStatus, Timestamp


@dataclass
class Detection:
    """检测数据实体"""
    id: int
    timestamp: Timestamp
    title: str
    message: str
    detection_type: DetectionType
    status: DetectionStatus = DetectionStatus.UNREAD
    url: Optional[str] = None
    user: Optional[str] = None
    
    def mark_as_read(self):
        """标记为已读"""
        self.status = DetectionStatus.READ
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'title': self.title,
            'message': self.message,
            'type': self.detection_type.value,
            'status': self.status.value,
            'url': self.url,
            'user': self.user
        }


