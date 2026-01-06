from flask import Flask, request, jsonify
import requests
from datetime import datetime
from typing import Optional


BASE = "http://iot.lwbsq.com"

def get_token(loginName: str, password: str) -> str:
    # 文档：GET /api/getToken，参数 loginName/password :contentReference[oaicite:13]{index=13}
    r = requests.get(f"{BASE}/api/getToken", params={"loginName": loginName, "password": password}, timeout=30)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 1000:
        raise RuntimeError(f"getToken failed: {j.get('message')}")
    return j["data"]["token"]

def get_realtime_data(token: str, groupId: Optional[str] = None):
    # 文档：GET /api/data/getRealTimeData，Header: authorization :contentReference[oaicite:14]{index=14}
    headers = {"authorization": token}
    params = {}
    if groupId:
        params["groupId"] = groupId
    r = requests.get(f"{BASE}/api/data/getRealTimeData", headers=headers, params=params, timeout=30)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 1000:
        raise RuntimeError(f"getRealTimeData failed: {j.get('message')}")
    return j["data"]

def flatten_device_item(dev: dict) -> dict:
    """
    把平台 dataItem/registerItem 摊平成好用结构：
    {
      deviceAddr: ...,
      deviceName: ...,
      timeStamp: ...,
      values: { "温度": 225, "湿度": 47.2, ... }
    }
    registerName/value/unit/alarmLevel 见文档字段 :contentReference[oaicite:15]{index=15}
    """
    out = {
        "deviceAddr": dev.get("deviceAddr"),
        "deviceName": dev.get("deviceName"),
        "deviceStatus": dev.get("deviceStatus"),
        "timeStamp": dev.get("timeStamp"),
        "timeStr": datetime.fromtimestamp((dev.get("timeStamp", 0) or 0)/1000).isoformat() if dev.get("timeStamp") else None,
        "values": {}
    }
    for node in (dev.get("dataItem") or []):
        for reg in (node.get("registerItem") or []):
            name = reg.get("registerName")
            val = reg.get("value")
            unit = reg.get("unit")
            alarm = reg.get("alarmLevel")
            if name:
                out["values"][name] = {"value": val, "unit": unit, "alarmLevel": alarm}
    return out


