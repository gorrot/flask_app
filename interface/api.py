from flask import Flask, request, jsonify
from datetime import datetime
from typing import Dict, Any

from application.detection_service import DetectionService
from application.stats_service import StatsService
from application.belt_service import BeltService
from application.sensor_service import SensorService
from infrastructure.repository import InMemoryDetectionRepository


def create_app() -> Flask:
    """创建 Flask 应用"""
    app = Flask(__name__)
    
    # 初始化依赖
    repository = InMemoryDetectionRepository(max_history=1000)
    detection_service = DetectionService(repository)
    stats_service = StatsService(repository)
    belt_service = BeltService(repository)
    sensor_service = SensorService()
    
    # ==================== 检测数据 API ====================
    
    @app.route('/receive_detection', methods=['POST'])
    def receive_detection():
        """接收来自PIVdata2.py的检测数据"""
        try:
            data = request.get_json()
            dtype = data.get('type', '未指定')
            required_fields = ['title', 'message']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'缺少必要字段: {field}'}), 400
            
            try:
                result = detection_service.receive_detection(
                    title=data['title'],
                    message=data['message'],
                    detection_type=data.get('type', 'mill_change'),
                    url=data.get('url'),
                    user=data.get('user')
                )
                if dtype in ('phase3_load_monitor', 'phase3_mill_status', 'phase3_mill_change'):
                    print(f"[三期] type={dtype} id={result.get('data_id')}")
            except Exception as save_error:
                print(f"❌ receive_detection 保存失败: {save_error}")
                return jsonify({'error': f'数据保存失败: {str(save_error)}'}), 500
            
            # 确保返回的数据可以正确序列化为JSON
            try:
                # 验证result是字典类型
                if not isinstance(result, dict):
                    print(f"⚠️ result不是字典类型: {type(result)}")
                    raise TypeError(f"result类型错误: {type(result)}")
                
                # 安全地转换data_id
                data_id = result.get('data_id', 0) or 0
                try:
                    data_id = int(data_id)
                except (ValueError, TypeError):
                    data_id = 0
                timestamp = result.get('timestamp', '')
                if timestamp is not None and not isinstance(timestamp, str):
                    timestamp = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
                timestamp = timestamp or ''
                safe_result = {
                    'status': 'success',
                    'message': str(result.get('message', '检测数据接收成功')),
                    'data_id': data_id,
                    'timestamp': timestamp
                }
                return jsonify(safe_result)
            except Exception as json_error:
                fallback_data_id = 0
                if isinstance(result, dict) and result.get('data_id') is not None:
                    try:
                        fallback_data_id = int(result.get('data_id', 0))
                    except (ValueError, TypeError):
                        pass
                return jsonify({'status': 'success', 'message': '检测数据已保存', 'data_id': fallback_data_id})
            
        except Exception as e:
            print(f"❌ receive_detection: {e}")
            return jsonify({'error': f'处理失败: {str(e)}'}), 500
    
    @app.route('/get_detections', methods=['GET'])
    def get_detections():
        """获取检测数据 - 手机APP调用"""
        try:
            data_type = request.args.get('type', 'all')
            limit = int(request.args.get('limit', 50))
            
            result = detection_service.get_detections(data_type, limit)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': f'获取数据失败: {str(e)}'}), 500

    @app.route('/recall/phase3', methods=['GET'])
    def recall_phase3():
        """三期数据召回检查：统计并返回 phase3 类型数量与最近若干条，用于排查 App 不显示"""
        try:
            types = ['phase3_load_monitor', 'phase3_mill_status', 'phase3_mill_change']
            counts = repository.count_by_types(types)
            last_n = min(int(request.args.get('limit', 10)), 50)
            items = repository.get_by_types(types, limit=last_n)
            return jsonify({
                'status': 'success',
                'phase3_load_monitor_count': counts.get('phase3_load_monitor', 0),
                'phase3_mill_status_count': counts.get('phase3_mill_status', 0),
                'phase3_mill_change_count': counts.get('phase3_mill_change', 0),
                'total_phase3': sum(counts.values()),
                'total_in_repo': repository.count_total(),
                'last_items': [d.to_dict() for d in items],
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/mark_read', methods=['POST'])
    def mark_read():
        """标记数据为已读"""
        try:
            data = request.get_json()
            data_id = data.get('id')
            
            if not data_id:
                return jsonify({'error': '缺少数据ID'}), 400
            
            result = detection_service.mark_as_read(data_id)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': f'标记失败: {str(e)}'}), 500
    
    @app.route('/get_stats', methods=['GET'])
    def get_stats():
        """获取统计信息"""
        try:
            result = stats_service.get_stats()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'获取统计失败: {str(e)}'}), 500
    
    @app.route('/get_belt_status', methods=['GET'])
    def get_belt_status():
        """获取当前皮带状态"""
        try:
            result = belt_service.get_belt_status()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'获取皮带状态失败: {str(e)}'}), 500
    
    # ==================== 传感器数据 API ====================
    
    @app.route("/api/token", methods=['GET'])
    def api_token():
        """获取传感器访问令牌（使用硬编码的账号密码）"""
        result = sensor_service.get_token()
        if result.get("ok"):
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    @app.route("/api/realtime", methods=['GET'])
    def api_realtime():
        """获取实时传感器数据（使用硬编码的账号密码）"""
        groupId = request.args.get("groupId")
        result = sensor_service.get_realtime_data(groupId=groupId)
        if result.get("ok"):
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    # ==================== 测试和健康检查 ====================
    
    @app.route('/test', methods=['GET', 'POST'])
    def test_endpoint():
        """测试接口"""
        if request.method == 'GET':
            return jsonify({
                'status': 'success',
                'message': 'Flask服务器运行正常',
                'timestamp': datetime.now().isoformat(),
                'total_data': repository.count_total()
            })
        
        elif request.method == 'POST':
            # 模拟接收检测数据
            result = detection_service.receive_detection(
                title='测试通知',
                message='这是一条测试消息',
                detection_type='test'
            )
            return jsonify({
                'status': 'success',
                'message': '测试数据已添加',
                'data_id': result['data_id']
            })
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'data_count': repository.count_total()
        })
    
    # 确保 repository 在闭包中可用（Python 闭包会自动捕获外部变量）
    
    return app

