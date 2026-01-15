import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.sensor_client import (
    get_token,
    get_realtime_data,
    flatten_device_item
)
from shared.config import get_config


class SensorService:
    """传感器数据服务用例"""
    
    def __init__(self):
        """初始化服务，从配置加载传感器凭证"""
        self.config = get_config()
        self.login_name, self.password = self.config.get_sensor_credentials()
        
        if not self.login_name or not self.password:
            raise ValueError(
                "传感器账号密码未配置！请设置环境变量 IOT_LOGIN_NAME 和 IOT_PASSWORD，"
                "或在 config.json 中配置 sensor.login_name 和 sensor.password"
            )
    
    def get_token(self) -> Dict[str, Any]:
        """获取传感器访问令牌"""
        try:
            token = get_token(self.login_name, self.password)
            return {"ok": True, "token": token}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def get_realtime_data(self, groupId: Optional[str] = None) -> Dict[str, Any]:
        """获取实时传感器数据"""
        try:
            token = get_token(self.login_name, self.password)
            raw = get_realtime_data(token, groupId=groupId)
            flat = [flatten_device_item(d) for d in raw]
            return {"ok": True, "count": len(flat), "data": flat}
        except Exception as e:
            return {"ok": False, "error": str(e)}



