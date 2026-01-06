from flask_cors import CORS
from interface.api import create_app

app = create_app()
CORS(app)  # 允许跨域请求

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
    # 启动命令: gunicorn -w 4 -b 0.0.0.0:5000 main:app
    app.run(host='0.0.0.0', port=5000, debug=True)  # 仅用于开发环境


