import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

BASE = "http://iot.lwbsq.com"


def get_token(loginName: str, password: str) -> str:
    """获取传感器访问令牌"""
    r = requests.get(
        f"{BASE}/api/getToken",
        params={"loginName": loginName, "password": password},
        timeout=30,
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
        timeout=30,
    )
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 1000:
        raise RuntimeError(f"getRealTimeData failed: {j.get('message')}")
    return j["data"]


def get_history_data(
    token: str,
    startTime: str,
    endTime: str,
    deviceAddr: str,
    nodeId: int = -1,
) -> list:
    """获取历史传感器数据（/api/data/historyList）。"""
    headers = {"authorization": token}
    params: Dict[str, Any] = {
        "deviceAddr": deviceAddr,
        "nodeId": nodeId,
        "startTime": startTime,
        "endTime": endTime,
    }

    r = requests.get(
        f"{BASE}/api/data/historyList",
        headers=headers,
        params=params,
        timeout=30,
    )
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 1000:
        raise RuntimeError(f"historyList failed: {j.get('message')}")

    data = j.get("data")
    if isinstance(data, list):
        return data
    return []


def flatten_device_item(dev: dict) -> Dict[str, Any]:
    """将平台 dataItem/registerItem 扁平化为易用结构。"""
    out = {
        "deviceAddr": dev.get("deviceAddr"),
        "deviceName": dev.get("deviceName"),
        "deviceStatus": dev.get("deviceStatus"),
        "timeStamp": dev.get("timeStamp"),
        "timeStr": datetime.fromtimestamp((dev.get("timeStamp", 0) or 0) / 1000).isoformat()
        if dev.get("timeStamp")
        else None,
        "values": {},
    }
    for node in (dev.get("dataItem") or []):
        for reg in (node.get("registerItem") or []):
            name = reg.get("registerName")
            if name:
                out["values"][name] = {
                    "value": reg.get("value"),
                    "unit": reg.get("unit"),
                    "alarmLevel": reg.get("alarmLevel"),
                }
    return out


def flatten_history_item(item: dict) -> List[Dict[str, Any]]:
    """将历史记录统一为扁平结构，便于 App 展示。"""
    ts = item.get("recordTime") or item.get("timeStamp") or 0
    time_str = item.get("recordTimeStr")
    if not time_str and ts:
        time_str = datetime.fromtimestamp((ts or 0) / 1000).strftime("%Y-%m-%d %H:%M:%S")

    device_addr = item.get("deviceAddr")
    node_id = item.get("nodeId")
    records = item.get("data")

    # 文档 3.3 返回 data 为数组，每条历史记录可包含多个寄存器值
    if isinstance(records, list) and records:
        out: List[Dict[str, Any]] = []
        for rec in records:
            out.append(
                {
                    "deviceAddr": device_addr,
                    "deviceName": item.get("deviceName"),
                    "nodeId": node_id,
                    "registerId": rec.get("registerId"),
                    "registerName": rec.get("registerName") or rec.get("dataName"),
                    "dataValue": rec.get("value"),
                    "dataText": rec.get("text"),
                    "unit": rec.get("unit"),
                    "alarmLevel": rec.get("alarmLevel"),
                    "recordTime": ts,
                    "recordTimeStr": time_str,
                    "recordId": item.get("recordId"),
                }
            )
        return out

    # 兼容旧结构
    return [
        {
            "deviceAddr": item.get("deviceAddr"),
            "deviceName": item.get("deviceName"),
            "nodeId": item.get("nodeId"),
            "registerId": item.get("registerId"),
            "registerName": item.get("registerName") or item.get("dataName"),
            "dataValue": item.get("dataValue") if item.get("dataValue") is not None else item.get("value"),
            "dataText": item.get("dataText") or item.get("text"),
            "unit": item.get("unit"),
            "alarmLevel": item.get("alarmLevel"),
            "recordTime": ts,
            "recordTimeStr": time_str,
            "recordId": item.get("recordId"),
        }
    ]