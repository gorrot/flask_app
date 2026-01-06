"""
测试脚本：验证所有检测类型都能正常创建
"""
from domain.rules import create_detection

# 测试所有 PIVdata2.py 发送的类型
test_types = [
    "mill_change",
    "b2_mill_change",
    "mill134_change",
    "belt_status",
    "empty_mill",
    "load_monitor",
    "test"
]

print("测试所有检测类型...")
print("=" * 50)

all_passed = True
for detection_type in test_types:
    try:
        detection = create_detection(
            title=f"测试 {detection_type}",
            message="测试消息",
            detection_type=detection_type
        )
        print(f"[OK] {detection_type:20s} -> {detection.detection_type.value}")
    except Exception as e:
        print(f"[FAIL] {detection_type:20s} -> 错误: {e}")
        all_passed = False

print("=" * 50)
if all_passed:
    print("[OK] 所有类型测试通过！")
else:
    print("[FAIL] 部分类型测试失败！")

