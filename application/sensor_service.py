from typing import Dict, Any, Optional
from infrastructure.sensor_client import (
    get_token,
    get_realtime_data,
    flatten_device_item
)

# 硬编码的用户名和密码（小型项目使用）
IOT_LOGIN_NAME = "vh251226gdcr"
IOT_PASSWORD = "vh251226gdcr"


class SensorService:
    """传感器数据服务用例"""
    
    def get_token(self) -> Dict[str, Any]:
        """获取传感器访问令牌"""
        try:
            token = get_token(IOT_LOGIN_NAME, IOT_PASSWORD)
            return {"ok": True, "token": token}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def get_realtime_data(self, groupId: Optional[str] = None) -> Dict[str, Any]:
        """获取实时传感器数据"""
        try:
            token = get_token(IOT_LOGIN_NAME, IOT_PASSWORD)
            raw = get_realtime_data(token, groupId=groupId)
            flat = [flatten_device_item(d) for d in raw]
            return {"ok": True, "count": len(flat), "data": flat}
        except Exception as e:
            return {"ok": False, "error": str(e)}


