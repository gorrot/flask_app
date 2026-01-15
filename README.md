# Flask 服务器重构说明

## 📁 项目结构

```
flask_server/
├── interface/              # 接口层（薄层）
│   ├── api.py             # 所有 Flask 路由
│   └── schemas.py         # 请求/响应 DTO
│
├── application/           # 应用层（用例）
│   ├── detection_service.py  # 检测数据用例
│   ├── stats_service.py      # 统计数据用例
│   ├── belt_service.py       # 皮带状态用例
│   └── sensor_service.py     # 传感器数据用例
│
├── domain/               # 领域层（业务逻辑）
│   ├── entities.py       # Detection / BeltStatus 等实体
│   ├── rules.py          # 业务规则 & 解析逻辑
│   └── value_objects.py  # Status / Type / Timestamp
│
├── infrastructure/       # 基础设施层
│   ├── repository.py      # InMemoryDetectionRepository
│   └── sensor_client.py  # get_token / get_realtime_data
│
├── main.py               # Flask 启动入口
├── requirements.txt      # 依赖包
└── test_api.py          # API 测试脚本
```

## 🚀 启动服务器

### 开发环境
```bash
cd flask_server
python main.py
```

### 生产环境（使用 Gunicorn）
```bash
cd flask_server
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 📋 API 端点

所有 API 端点保持不变，确保向后兼容：

- `POST /receive_detection` - 接收检测数据（PIVdata2.py 使用）
- `GET /get_detections` - 获取检测数据（Android APP 使用）
- `POST /mark_read` - 标记已读
- `GET /get_stats` - 获取统计信息
- `GET /get_belt_status` - 获取皮带状态
- `GET /api/token` - 获取传感器访问令牌
- `GET /api/realtime` - 获取实时传感器数据
- `GET /test` - 测试接口
- `GET /health` - 健康检查

## ✅ 向后兼容性

- ✅ 所有 API 端点路径保持不变
- ✅ 请求/响应格式保持不变
- ✅ PIVdata2.py 无需修改
- ✅ GUI1.py 无需修改
- ✅ Android APP 无需修改

## 🧪 测试

运行测试脚本验证所有端点：

```bash
# 1. 启动服务器（在另一个终端）
python main.py

# 2. 运行测试（在新终端）
python test_api.py
```

## 📦 依赖安装

```bash
pip install -r requirements.txt
```

## 🔄 从旧版本迁移

旧版本的 `app.py` 和 `contact.py` 已被重构到新结构中：

- `app.py` → `interface/api.py` + `application/*.py` + `domain/*.py` + `infrastructure/repository.py`
- `contact.py` → `infrastructure/sensor_client.py`

**无需修改任何调用代码**，所有功能保持不变。

## 🏗️ 架构说明

### 分层架构

1. **Interface 层**：薄层，只负责 HTTP 请求/响应处理
2. **Application 层**：用例服务，实现业务用例
3. **Domain 层**：核心业务逻辑，实体和规则
4. **Infrastructure 层**：技术实现，数据存储和外部服务

### 优势

- ✅ 代码组织清晰，易于维护
- ✅ 各层职责明确，易于测试
- ✅ 易于扩展新功能
- ✅ 向后兼容，无需修改现有代码



