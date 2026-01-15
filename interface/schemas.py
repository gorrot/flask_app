from typing import Optional
from dataclasses import dataclass


@dataclass
class DetectionRequest:
    """检测数据请求DTO"""
    title: str
    message: str
    type: Optional[str] = "mill_change"
    url: Optional[str] = None
    user: Optional[str] = None
    timestamp: Optional[str] = None  # 可选，服务端会生成


@dataclass
class MarkReadRequest:
    """标记已读请求DTO"""
    id: int



