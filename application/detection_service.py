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
            print(f"📨 收到检测数据: {title}")
            
            # 安全地获取ID，确保是int类型
            try:
                detection_id = int(saved_detection.id)
            except (ValueError, TypeError) as e:
                print(f"⚠️ ID转换失败: {e}，使用时间戳作为ID")
                detection_id = int(datetime.now().timestamp() * 1000)
            
            # 安全地获取时间戳字符串
            try:
                timestamp_str = saved_detection.timestamp.isoformat()
                # 确保是字符串类型
                if not isinstance(timestamp_str, str):
                    timestamp_str = str(timestamp_str)
            except Exception as e:
                print(f"⚠️ 时间戳转换失败: {e}，使用当前时间")
                timestamp_str = datetime.now().isoformat()
            
            # 确保返回值的所有字段都是可序列化的类型
            return {
                'status': 'success',
                'message': '检测数据接收成功',
                'data_id': detection_id,  # 确保是int
                'timestamp': timestamp_str  # 确保是str
            }
        except Exception as e:
            print(f"❌ DetectionService.receive_detection 内部错误: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_detections(
        self,
        data_type: str = 'all',
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取检测数据"""
        if data_type == 'unread':
            detections = self.repository.get_unread(limit)
        else:
            detections = self.repository.get_all(limit)
        
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



