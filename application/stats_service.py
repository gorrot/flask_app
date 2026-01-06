from typing import Dict, Any
from datetime import datetime
from infrastructure.repository import InMemoryDetectionRepository


class StatsService:
    """统计服务用例"""
    
    def __init__(self, repository: InMemoryDetectionRepository):
        self.repository = repository
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        all_detections = self.repository.get_all_detections()
        total_count = len(all_detections)
        unread_count = self.repository.count_unread()
        
        # 按类型统计
        type_stats = {}
        for detection in all_detections:
            data_type = detection.detection_type.value
            type_stats[data_type] = type_stats.get(data_type, 0) + 1
        
        # 按任务（URL+User）统计
        task_stats = {}
        for detection in all_detections:
            task_key = f"{detection.url or '未知URL'} | {detection.user or '未知用户'}"
            if task_key not in task_stats:
                task_stats[task_key] = {
                    'url': detection.url,
                    'user': detection.user,
                    'total': 0,
                    'unread': 0,
                    'by_type': {}
                }
            task_stats[task_key]['total'] += 1
            if detection.status.value == 'unread':
                task_stats[task_key]['unread'] += 1
            # 按类型统计每个任务
            data_type = detection.detection_type.value
            task_stats[task_key]['by_type'][data_type] = (
                task_stats[task_key]['by_type'].get(data_type, 0) + 1
            )
        
        return {
            'status': 'success',
            'stats': {
                'total_detections': total_count,
                'unread_detections': unread_count,
                'type_statistics': type_stats,
                'task_statistics': task_stats,
                'last_update': datetime.now().isoformat()
            }
        }


