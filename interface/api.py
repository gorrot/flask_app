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
            
            # 验证必要字段
            required_fields = ['title', 'message']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'缺少必要字段: {field}'}), 400
            
            result = detection_service.receive_detection(
                title=data['title'],
                message=data['message'],
                detection_type=data.get('type', 'mill_change'),
                url=data.get('url'),
                user=data.get('user')
            )
            return jsonify(result)
            
        except Exception as e:
            print(f"❌ 处理检测数据失败: {e}")
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

