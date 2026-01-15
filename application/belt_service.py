from typing import Dict, Any
from datetime import datetime
from domain.value_objects import DetectionType
from domain.rules import parse_belt_status_message
from infrastructure.repository import InMemoryDetectionRepository


class BeltService:
    """皮带状态服务用例"""
    
    def __init__(self, repository: InMemoryDetectionRepository):
        self.repository = repository
    
    def get_belt_status(self) -> Dict[str, Any]:
        """获取当前皮带状态"""
        all_detections = self.repository.get_all_detections()
        
        # 查找所有belt_status类型的数据
        belt_data_list = [
            d for d in all_detections 
            if d.detection_type == DetectionType.BELT_STATUS
        ]
        
        if not belt_data_list:
            return {
                'status': 'success',
                'belt_status': {},
                'message': '暂无皮带状态数据'
            }
        
        # 从所有belt_status数据中提取每个皮带的最新状态
        belt_status_map = {}
        belt_timestamps = {}
        
        for belt_data in belt_data_list:
            message = belt_data.message
            timestamp = belt_data.timestamp.isoformat()
            
            # 解析消息，提取皮带名称和最新状态
            parsed_statuses = parse_belt_status_message(message)
            
            for belt_name, status in parsed_statuses.items():
                # 只保留最新的状态（按时间戳）
                if belt_name not in belt_timestamps or timestamp > belt_timestamps[belt_name]:
                    belt_status_map[belt_name] = status
                    belt_timestamps[belt_name] = timestamp
        
        # 获取最新的更新时间
        latest_timestamp = (
            max(belt_timestamps.values()) 
            if belt_timestamps 
            else datetime.now().isoformat()
        )
        
        return {
            'status': 'success',
            'belt_status': belt_status_map,
            'last_update': latest_timestamp,
            'message': '皮带状态数据'
        }



