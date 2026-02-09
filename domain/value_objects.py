from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DetectionType(str, Enum):
    """检测类型枚举"""
    MILL_CHANGE = "mill_change"
    MILL134_CHANGE = "mill134_change"  # 1,3,4炉倒磨检测
    B2_MILL_CHANGE = "b2_mill_change"  # 2炉倒磨检测
    BELT_STATUS = "belt_status"
    EMPTY_MILL = "empty_mill"
    LOAD_MONITOR = "load_monitor"  # 负载监控
    PHASE3_LOAD_MONITOR = "phase3_load_monitor"  # 三期 #5-#8 机组负荷
    PHASE3_MILL_STATUS = "phase3_mill_status"    # 三期 #5-#8 磨煤机状态
    PHASE3_MILL_CHANGE = "phase3_mill_change"    # 三期 #5-#8 倒磨检测
    TEST = "test"


class DetectionStatus(str, Enum):
    """检测状态枚举"""
    UNREAD = "unread"
    READ = "read"


@dataclass
class Timestamp:
    """时间戳值对象"""
    value: datetime
    
    @classmethod
    def now(cls) -> 'Timestamp':
        return cls(datetime.now())
    
    def isoformat(self) -> str:
        return self.value.isoformat()

