import sys
from pathlib import Path

# 添加项目根目录到Python路径，以便导入shared模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask_cors import CORS
from interface.api import create_app
from shared.config import get_config

# 加载配置
config = get_config()

app = create_app()
CORS(app)  # 允许跨域请求

if __name__ == '__main__':
    flask_config = config.get("flask", {})
    host = flask_config.get("host", "0.0.0.0")
    port = flask_config.get("port", 5000)
    debug = flask_config.get("debug", False)
    base_url = flask_config.get("base_url", f"http://{host}:{port}")
    
    print("🚀 Flask检测数据服务器启动中...")
    print("📱 等待检测数据和手机APP连接...")
    print(f"🔗 服务器地址: {base_url}")
    print("📋 可用接口:")
    print("   POST /receive_detection - 接收检测数据")
    print("   GET  /get_detections - 获取检测数据")
    print("   GET  /recall/phase3 - 三期数据召回检查（排查不显示）")
    print("   POST /mark_read - 标记已读")
    print("   GET  /get_stats - 获取统计信息")
    print("   GET  /get_belt_status - 获取皮带状态")
    print("   GET  /api/token - 获取传感器访问令牌")
    print("   GET  /api/realtime - 获取实时传感器数据")
    print("   GET  /test - 测试接口")
    print("   GET  /health - 健康检查")
    print(f"\n⚙️  配置来源: {config.config_file if hasattr(config, 'config_file') else '环境变量/默认值'}")
    
    # 生产环境请使用 gunicorn 启动，不要使用 debug=True
    # 启动命令: gunicorn -w 4 -b 0.0.0.0:5000 main:app
    app.run(host=host, port=port, debug=debug)



