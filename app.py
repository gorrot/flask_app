from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from datetime import datetime
import threading
import queue
from contact import get_token, get_realtime_data, flatten_device_item

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据存储
detection_data = []
data_lock = threading.Lock()


class DetectionDataManager:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.max_history = 1000  # 最多保存1000条记录

    def add_detection(self, title, message, detection_type="mill_change", url=None, user=None):
        """添加检测数据"""
        data = {
            'id': int(time.time() * 1000),  # 使用时间戳作为ID
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'type': detection_type,
            'status': 'unread',  # unread, read
            'url': url,  # 任务URL标识
            'user': user  # 任务用户标识
        }

        with data_lock:
            detection_data.append(data)
            # 保持数据量在合理范围内
            if len(detection_data) > self.max_history:
                detection_data.pop(0)

        print(f"📨 收到检测数据: {title}")
        return data

    def get_unread_data(self, limit=50):
        """获取未读数据"""
        with data_lock:
            unread_data = [d for d in detection_data if d['status'] == 'unread']
            return unread_data[-limit:] if unread_data else []

    def get_all_data(self, limit=50):
        """获取所有数据"""
        with data_lock:
            return detection_data[-limit:] if detection_data else []

    def get_data_by_types(self, types, limit=50):
        """按类型过滤并返回数据，多类型时每类至少保留最新一条，避免 belt_status 等被挤出"""
        if not types:
            return self.get_all_data(limit)
        with data_lock:
            type_set = set(types)
            filtered = [d for d in detection_data if d.get('type') in type_set]
            if not filtered:
                return []
            n = len(types)
            quota = max(1, (limit + n - 1) // n)
            by_type = {}
            for t in types:
                by_type[t] = [d for d in filtered if d.get('type') == t]
            result = []
            for t in types:
                result.extend(by_type[t][-quota:])
            result.sort(key=lambda d: d.get('id', 0), reverse=True)
            return result[:limit]

    def mark_as_read(self, data_id):
        """标记数据为已读"""
        with data_lock:
            for data in detection_data:
                if data['id'] == data_id:
                    data['status'] = 'read'
                    break


# 全局数据管理器
data_manager = DetectionDataManager()




@app.route('/receive_detection', methods=['POST'])
def receive_detection():
    """接收来自PIVdata2.py的检测数据"""
    try:
        data = request.get_json()

        # 验证必要字段
        required_fields = ['title', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400

        title = data['title']
        message = data['message']
        detection_type = data.get('type', 'mill_change')
        url = data.get('url')  # 获取任务URL
        user = data.get('user')  # 获取任务用户

        # 添加检测数据
        detection = data_manager.add_detection(title, message, detection_type, url=url, user=user)

        return jsonify({
            'status': 'success',
            'message': '检测数据接收成功',
            'data_id': detection['id'],
            'timestamp': detection['timestamp']
        })

    except Exception as e:
        print(f"❌ 处理检测数据失败: {e}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500


@app.route('/get_detections', methods=['GET'])
def get_detections():
    """获取检测数据 - 手机APP调用。支持 type=all / unread / 逗号分隔类型(如 load_monitor,belt_status)。"""
    try:
        data_type = request.args.get('type', 'all')
        limit = int(request.args.get('limit', 50))

        if data_type == 'unread':
            data = data_manager.get_unread_data(limit)
        elif data_type == 'all':
            data = data_manager.get_all_data(limit)
        else:
            # 按请求的类型过滤，确保 belt_status 等类型能被返回
            types = [t.strip() for t in data_type.split(',') if t.strip()]
            data = data_manager.get_data_by_types(types, limit)

        return jsonify({
            'status': 'success',
            'data': data,
            'total_count': len(data),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'获取数据失败: {str(e)}'}), 500


@app.route('/mark_read', methods=['POST'])
def mark_read():
    """标记数据为已读"""
    try:
        data = request.get_json()
        data_id = data.get('id')

        if not data_id:
            return jsonify({'error': '缺少数据ID'}), 400

        data_manager.mark_as_read(data_id)

        return jsonify({
            'status': 'success',
            'message': '标记成功'
        })

    except Exception as e:
        return jsonify({'error': f'标记失败: {str(e)}'}), 500


@app.route('/get_stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    try:
        with data_lock:
            total_count = len(detection_data)
            unread_count = len([d for d in detection_data if d['status'] == 'unread'])

            # 按类型统计
            type_stats = {}
            for data in detection_data:
                data_type = data['type']
                type_stats[data_type] = type_stats.get(data_type, 0) + 1

            # 按任务（URL+User）统计
            task_stats = {}
            for data in detection_data:
                task_key = f"{data.get('url', '未知URL')} | {data.get('user', '未知用户')}"
                if task_key not in task_stats:
                    task_stats[task_key] = {
                        'url': data.get('url'),
                        'user': data.get('user'),
                        'total': 0,
                        'unread': 0,
                        'by_type': {}
                    }
                task_stats[task_key]['total'] += 1
                if data['status'] == 'unread':
                    task_stats[task_key]['unread'] += 1
                # 按类型统计每个任务
                data_type = data['type']
                task_stats[task_key]['by_type'][data_type] = task_stats[task_key]['by_type'].get(data_type, 0) + 1

        return jsonify({
            'status': 'success',
            'stats': {
                'total_detections': total_count,
                'unread_detections': unread_count,
                'type_statistics': type_stats,
                'task_statistics': task_stats,  # 新增：按任务统计
                'last_update': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({'error': f'获取统计失败: {str(e)}'}), 500


@app.route('/get_belt_status', methods=['GET'])
def get_belt_status():
    """获取当前皮带状态（从所有belt_status数据中提取每个皮带的最新状态）"""
    try:
        with data_lock:
            # 查找所有belt_status类型的数据
            belt_data_list = [d for d in detection_data if d.get('type') == 'belt_status']
            
            if not belt_data_list:
                return jsonify({
                    'status': 'success',
                    'belt_status': {},
                    'message': '暂无皮带状态数据'
                })
            
            # 从所有belt_status数据中提取每个皮带的最新状态
            # 使用字典记录每个皮带的最新状态（按时间戳排序）
            belt_status_map = {}
            belt_timestamps = {}  # 记录每个皮带的最新时间戳
            
            # 遍历所有belt_status数据，提取每个皮带的最新状态
            for belt_data in belt_data_list:
                message = belt_data.get('message', '')
                timestamp = belt_data.get('timestamp', '')
                title = belt_data.get('title', '')
                
                # 解析消息，提取皮带名称和最新状态
                lines = message.split('\n')
                for line in lines:
                    if '▸' in line:
                        try:
                            belt_name = None
                            status = None
                            
                            # 格式1：  ▸ 皮带名称: 旧状态 → 新状态 (检测时间: 14:30:25) - 变化消息
                            if '→' in line:
                                parts = line.split('→')
                                if len(parts) == 2:
                                    belt_part = parts[0].split('▸')[1].strip()
                                    belt_name = belt_part.split(':')[0].strip()
                                    status = parts[1].split('(')[0].strip()
                            
                            # 格式2：  ▸ 皮带名称: 状态 (当前状态) - 当前状态消息
                            elif '(当前状态)' in line:
                                belt_part = line.split('▸')[1].strip()
                                if ':' in belt_part:
                                    belt_name = belt_part.split(':')[0].strip()
                                    status = belt_part.split(':')[1].split('(')[0].strip()
                            
                            if belt_name and status:
                                # 只保留最新的状态（按时间戳）
                                if belt_name not in belt_timestamps or timestamp > belt_timestamps[belt_name]:
                                    belt_status_map[belt_name] = status
                                    belt_timestamps[belt_name] = timestamp
                        except Exception as e:
                            print(f"解析皮带状态失败: {line}, 错误: {e}")
            
            # 获取最新的更新时间
            latest_timestamp = max(belt_timestamps.values()) if belt_timestamps else datetime.now().isoformat()
            
            return jsonify({
                'status': 'success',
                'belt_status': belt_status_map,
                'last_update': latest_timestamp,
                'message': '皮带状态数据'
            })
    
    except Exception as e:
        return jsonify({'error': f'获取皮带状态失败: {str(e)}'}), 500


@app.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    """测试接口"""
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'message': 'Flask服务器运行正常',
            'timestamp': datetime.now().isoformat(),
            'total_data': len(detection_data)
        })

    elif request.method == 'POST':
        # 模拟接收检测数据
        test_data = {
            'title': '测试通知',
            'message': '这是一条测试消息',
            'type': 'test'
        }

        detection = data_manager.add_detection(
            test_data['title'],
            test_data['message'],
            test_data['type']
        )

        return jsonify({
            'status': 'success',
            'message': '测试数据已添加',
            'data': detection
        })


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_count': len(detection_data)
    })


# ==================== 传感器数据 API ====================

# 硬编码的用户名和密码（小型项目使用）
IOT_LOGIN_NAME = "vh251226gdcr"
IOT_PASSWORD = "vh251226gdcr"


@app.get("/api/token")
def api_token():
    """获取传感器访问令牌（使用硬编码的账号密码）"""
    try:
        token = get_token(IOT_LOGIN_NAME, IOT_PASSWORD)
        return jsonify({"ok": True, "token": token})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/api/realtime")
def api_realtime():
    """
    获取实时传感器数据（使用硬编码的账号密码）
    用法示例：
    /api/realtime
    或 /api/realtime?groupId=xxx（可选参数）
    """
    groupId = request.args.get("groupId")  # groupId 仍然是可选的 URL 参数

    try:
        token = get_token(IOT_LOGIN_NAME, IOT_PASSWORD)
        raw = get_realtime_data(token, groupId=groupId)
        flat = [flatten_device_item(d) for d in raw]
        return jsonify({"ok": True, "count": len(flat), "data": flat})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == '__main__':
    print("🚀 Flask检测数据服务器启动中...")
    print("📱 等待检测数据和手机APP连接...")
    print("🔗 服务器地址: http://localhost:5000")
    print("📋 可用接口:")
    print("   POST /receive_detection - 接收检测数据")
    print("   GET  /get_detections - 获取检测数据")
    print("   POST /mark_read - 标记已读")
    print("   GET  /get_stats - 获取统计信息")
    print("   GET  /get_belt_status - 获取皮带状态")
    print("   GET  /api/token - 获取传感器访问令牌")
    print("   GET  /api/realtime - 获取实时传感器数据（使用硬编码账号）")
    print("   GET  /test - 测试接口")
    print("   GET  /health - 健康检查")

    # 生产环境请使用 gunicorn 启动，不要使用 debug=True
    # 启动命令: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    app.run(host='0.0.0.0', port=5000, debug=True)  # 仅用于开发环境
