from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from infrastructure.sensor_client import (
    get_token,
    get_realtime_data,
    get_history_data,
    flatten_device_item,
    flatten_history_item,
)

# 传感器平台账号密码（与当前项目保持一致）
IOT_LOGIN_NAME = "vh251226gdcr"
IOT_PASSWORD = "vh251226gdcr"


class SensorService:
    """传感器数据服务用例"""

    def __init__(self):
        self.login_name = IOT_LOGIN_NAME
        self.password = IOT_PASSWORD

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

    def get_recent_history(
        self,
        days: int = 7,
        groupId: Optional[str] = None,
        deviceAddr: Optional[str] = None,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """获取最近 N 天历史数据（默认 7 天）。"""
        try:
            safe_days = max(1, min(days, 30))
            safe_limit = max(1, min(limit, 5000))

            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=safe_days)
            start_ms = int(start_dt.timestamp() * 1000)
            end_ms = int(end_dt.timestamp() * 1000)

            token = get_token(self.login_name, self.password)
            raw = get_history_data(
                token=token,
                startTime=start_ms,
                endTime=end_ms,
                groupId=groupId,
                deviceAddr=deviceAddr,
                limit=safe_limit,
            )
            flat = [flatten_history_item(d) for d in raw]
            flat.sort(key=lambda x: x.get("recordTime") or 0, reverse=True)

            return {
                "ok": True,
                "days": safe_days,
                "startTime": start_ms,
                "endTime": end_ms,
                "count": len(flat),
                "data": flat,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
