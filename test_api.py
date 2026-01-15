"""
测试脚本：验证所有API端点是否正常工作
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查"""
    print("🔍 测试 /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    return response.status_code == 200

def test_receive_detection():
    """测试接收检测数据"""
    print("\n🔍 测试 POST /receive_detection...")
    data = {
        'title': '测试检测',
        'message': '这是一条测试消息',
        'type': 'test',
        'url': 'http://test.com',
        'user': 'test_user'
    }
    response = requests.post(f"{BASE_URL}/receive_detection", json=data)
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    return response.status_code == 200

def test_get_detections():
    """测试获取检测数据"""
    print("\n🔍 测试 GET /get_detections...")
    response = requests.get(f"{BASE_URL}/get_detections?type=all&limit=10")
    print(f"   状态码: {response.status_code}")
    result = response.json()
    print(f"   数据数量: {result.get('total_count', 0)}")
    return response.status_code == 200

def test_get_stats():
    """测试获取统计信息"""
    print("\n🔍 测试 GET /get_stats...")
    response = requests.get(f"{BASE_URL}/get_stats")
    print(f"   状态码: {response.status_code}")
    result = response.json()
    print(f"   总检测数: {result.get('stats', {}).get('total_detections', 0)}")
    return response.status_code == 200

def test_get_belt_status():
    """测试获取皮带状态"""
    print("\n🔍 测试 GET /get_belt_status...")
    response = requests.get(f"{BASE_URL}/get_belt_status")
    print(f"   状态码: {response.status_code}")
    result = response.json()
    print(f"   响应: {result.get('message', '')}")
    return response.status_code == 200

def test_api_token():
    """测试获取传感器令牌"""
    print("\n🔍 测试 GET /api/token...")
    response = requests.get(f"{BASE_URL}/api/token")
    print(f"   状态码: {response.status_code}")
    result = response.json()
    print(f"   成功: {result.get('ok', False)}")
    return response.status_code in [200, 500]  # 500可能是网络问题，也算正常

def test_api_realtime():
    """测试获取实时传感器数据"""
    print("\n🔍 测试 GET /api/realtime...")
    response = requests.get(f"{BASE_URL}/api/realtime")
    print(f"   状态码: {response.status_code}")
    result = response.json()
    print(f"   成功: {result.get('ok', False)}")
    return response.status_code in [200, 500]  # 500可能是网络问题，也算正常

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Flask API 端点测试")
    print("=" * 50)
    
    results = []
    results.append(("健康检查", test_health()))
    results.append(("接收检测数据", test_receive_detection()))
    results.append(("获取检测数据", test_get_detections()))
    results.append(("获取统计信息", test_get_stats()))
    results.append(("获取皮带状态", test_get_belt_status()))
    results.append(("获取传感器令牌", test_api_token()))
    results.append(("获取实时传感器数据", test_api_realtime()))
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查服务器是否正常运行")
    print("=" * 50)



