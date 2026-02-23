import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

BASE = "http://iot.lwbsq.com"


def get_token(loginName: str, password: str) -> str:
    """获取传感器访问令牌"""
    r = requests.get(
        f"{BASE}/api/getToken",
        params={"loginName": loginName, "password": password},
        timeout=30
    )
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 1000:
        raise RuntimeError(f"getToken failed: {j.get('message')}")
    return j["data"]["token"]


def get_realtime_data(token: str, groupId: Optional[str] = None) -> list:
    """获取实时传感器数据"""
    headers = {"authorization": token}
    params = {}
    if groupId:
        params["groupId"] = groupId
    r = requests.get(
        f"{BASE}/api/data/getRealTimeData",
        headers=headers,
        params=params,
        timeout=30
    )
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 1000:
        raise RuntimeError(f"getRealTimeData failed: {j.get('message')}")
    return j["data"]


def get_history_data(
    token: str,
    startTime: int,
    endTime: int,
    groupId: Optional[str] = None,
    deviceAddr: Optional[str] = None,
    limit: int = 1000,
) -> list:
    """获取历史传感器数据（/api/data/historyList）"""
    headers = {"authorization": token}
    params: Dict[str, Any] = {
        "startTime": startTime,
        "endTime": endTime,
        "limit": limit,
    }
    if groupId:
        params["groupId"] = groupId
    if deviceAddr:
        params["deviceAddr"] = deviceAddr

    r = requests.get(
        f"{BASE}/api/data/historyList",
        headers=headers,
        params=params,
        timeout=30
    )
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 1000:
        raise RuntimeError(f"historyList failed: {j.get('message')}")

    data = j.get("data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("list", "records", "rows", "data"):
            v = data.get(key)
            if isinstance(v, list):
                return v
    return []


def flatten_device_item(dev: dict) -> Dict[str, Any]:
    """
    把平台 dataItem/registerItem 摊平成好用结构
    """
    out = {
        "deviceAddr": dev.get("deviceAddr"),
        "deviceName": dev.get("deviceName"),
        "deviceStatus": dev.get("deviceStatus"),
        "timeStamp": dev.get("timeStamp"),
        "timeStr": datetime.fromtimestamp(
            (dev.get("timeStamp", 0) or 0) / 1000
        ).isoformat() if dev.get("timeStamp") else None,
        "values": {}
    }
    for node in (dev.get("dataItem") or []):
        for reg in (node.get("registerItem") or []):
            name = reg.get("registerName")
            val = reg.get("value")
            unit = reg.get("unit")
            alarm = reg.get("alarmLevel")
            if name:
                out["values"][name] = {
                    "value": val,
                    "unit": unit,
                    "alarmLevel": alarm
                }
    return out


def flatten_history_item(item: dict) -> Dict[str, Any]:
    """将历史记录统一为扁平结构，便于 App 展示。"""
    ts = item.get("recordTime") or item.get("timeStamp") or 0
    out = {
        "deviceAddr": item.get("deviceAddr"),
        "deviceName": item.get("deviceName"),
        "registerName": item.get("registerName") or item.get("dataName"),
        "dataValue": item.get("dataValue") if item.get("dataValue") is not None else item.get("value"),
        "dataText": item.get("dataText"),
        "unit": item.get("unit"),
        "alarmLevel": item.get("alarmLevel"),
        "recordTime": ts,
        "recordTimeStr": item.get("recordTimeStr"),
    }
    if not out["recordTimeStr"] and ts:
        out["recordTimeStr"] = datetime.fromtimestamp((ts or 0) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    return out



