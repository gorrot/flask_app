from typing import Dict, Any, Optional
from datetime import datetime
from domain.rules import create_detection
from infrastructure.repository import InMemoryDetectionRepository


class DetectionService:
    """检测数据服务用例"""
    
    def __init__(self, repository: InMemoryDetectionRepository):
        self.repository = repository
    
    def receive_detection(
        self,
        title: str,
        message: str,
        detection_type: str = "mill_change",
        url: Optional[str] = None,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """接收检测数据"""
        try:
            detection = create_detection(
                title=title,
                message=message,
                detection_type=detection_type,
                url=url,
                user=user
            )
            
            saved_detection = self.repository.add(detection)
            try:
                detection_id = int(saved_detection.id)
            except (ValueError, TypeError):
                detection_id = int(datetime.now().timestamp() * 1000)
            try:
                timestamp_str = saved_detection.timestamp.isoformat()
                if not isinstance(timestamp_str, str):
                    timestamp_str = str(timestamp_str)
            except Exception:
                timestamp_str = datetime.now().isoformat()
            
            # 确保返回值的所有字段都是可序列化的类型
            return {
                'status': 'success',
                'message': '检测数据接收成功',
                'data_id': detection_id,  # 确保是int
                'timestamp': timestamp_str  # 确保是str
            }
        except Exception as e:
            raise
    
    def get_detections(
        self,
        data_type: str = 'all',
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取检测数据。data_type 为 all/unread 时按原逻辑；否则按逗号分隔的类型过滤（如 phase3_load_monitor,phase3_mill_status）。"""
        if data_type == 'unread':
            detections = self.repository.get_unread(limit)
        elif data_type == 'all':
            detections = self.repository.get_all(limit)
        else:
            types = [t.strip() for t in data_type.split(',') if t.strip()]
            # 多类型时使用固定配额：每种类型最多 ceil(limit/类型数) 条，从机制上根除少类型被挤出
            if len(types) > 1:
                detections = self.repository.get_by_types_balanced(types, limit=limit)
            else:
                detections = self.repository.get_by_types(types, limit)
        
        return {
            'status': 'success',
            'data': [d.to_dict() for d in detections],
            'total_count': len(detections),
            'timestamp': datetime.now().isoformat()
        }
    
    def mark_as_read(self, data_id: int) -> Dict[str, Any]:
        """标记数据为已读"""
        success = self.repository.mark_as_read(data_id)
        if success:
            return {
                'status': 'success',
                'message': '标记成功'
            }
        else:
            return {
                'status': 'error',
                'message': '数据不存在'
            }



