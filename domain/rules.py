from typing import Dict, Optional
from datetime import datetime
from domain.entities import Detection
from domain.value_objects import DetectionType, DetectionStatus, Timestamp


def parse_belt_status_message(message: str) -> Dict[str, str]:
    """
    解析皮带状态消息，提取每个皮带的最新状态
    格式1: ▸ 皮带名称: 旧状态 → 新状态 (检测时间: 14:30:25)
    格式2: ▸ 皮带名称: 状态 (当前状态)
    """
    belt_status_map = {}
    lines = message.split('\n')
    
    for line in lines:
        if '▸' not in line:
            continue
        
        try:
            belt_name = None
            status = None
            
            # 格式1：变化消息
            if '→' in line:
                parts = line.split('→')
                if len(parts) == 2:
                    belt_part = parts[0].split('▸')[1].strip()
                    belt_name = belt_part.split(':')[0].strip()
                    status = parts[1].split('(')[0].strip()
            
            # 格式2：当前状态消息
            elif '(当前状态)' in line:
                belt_part = line.split('▸')[1].strip()
                if ':' in belt_part:
                    belt_name = belt_part.split(':')[0].strip()
                    status = belt_part.split(':')[1].split('(')[0].strip()
            
            if belt_name and status:
                belt_status_map[belt_name] = status
        except Exception as e:
            print(f"解析皮带状态失败: {line}, 错误: {e}")
    
    return belt_status_map


def create_detection(
    title: str,
    message: str,
    detection_type: str = "mill_change",
    url: Optional[str] = None,
    user: Optional[str] = None
) -> Detection:
    """创建检测实体"""
    detection_id = int(datetime.now().timestamp() * 1000)
    
    # 尝试转换为枚举，如果失败则使用默认值
    try:
        detection_type_enum = DetectionType(detection_type)
    except ValueError:
        # 如果类型不在枚举中，使用默认值并打印警告
        print(f"⚠️ 警告: 未知的检测类型 '{detection_type}'，使用默认类型 'mill_change'")
        detection_type_enum = DetectionType.MILL_CHANGE
    
    return Detection(
        id=detection_id,
        timestamp=Timestamp.now(),
        title=title,
        message=message,
        detection_type=detection_type_enum,
        status=DetectionStatus.UNREAD,
        url=url,
        user=user
    )

