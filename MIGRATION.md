# 重构迁移指南

## ✅ 重构完成

Flask 服务器已成功重构为分层架构，所有功能保持不变，**完全向后兼容**。

## 📋 变更说明

### 新的启动方式

**旧方式（仍可用）：**
```bash
python app.py
```

**新方式（推荐）：**
```bash
python main.py
```

### 文件映射

| 旧文件 | 新位置 | 说明 |
|--------|--------|------|
| `app.py` | `interface/api.py` + `application/*.py` + `domain/*.py` + `infrastructure/repository.py` | 路由和业务逻辑已拆分 |
| `contact.py` | `infrastructure/sensor_client.py` | 传感器客户端功能 |

### API 端点

**所有 API 端点保持不变**，无需修改任何调用代码：

- ✅ `POST /receive_detection` - PIVdata2.py 使用
- ✅ `GET /get_detections` - Android APP 使用
- ✅ `POST /mark_read` - Android APP 使用
- ✅ `GET /get_stats` - Android APP 使用
- ✅ `GET /get_belt_status` - Android APP 使用
- ✅ `GET /api/token` - Android APP 使用
- ✅ `GET /api/realtime` - Android APP 使用
- ✅ `GET /test` - 测试接口
- ✅ `GET /health` - 健康检查

## 🔄 迁移步骤

### 1. 安装依赖（如未安装）

```bash
cd flask_server
pip install -r requirements.txt
```

### 2. 启动服务器

**开发环境：**
```bash
python main.py
```

**生产环境（使用 Gunicorn）：**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 3. 验证功能

运行测试脚本：
```bash
# 在另一个终端运行
python test_api.py
```

## ✅ 兼容性验证

- ✅ **PIVdata2.py**：无需修改，继续使用 `POST /receive_detection`
- ✅ **GUI1.py**：无需修改，继续使用相同的 Flask 服务器地址
- ✅ **Android APP**：无需修改，所有 API 端点保持不变

## 📁 新项目结构

```
flask_server/
├── interface/          # 接口层（路由）
├── application/        # 应用层（用例服务）
├── domain/             # 领域层（业务逻辑）
├── infrastructure/     # 基础设施层（数据存储、外部服务）
├── main.py            # 启动入口
└── requirements.txt   # 依赖包
```

## 🎯 优势

1. **代码组织清晰**：分层架构，职责明确
2. **易于维护**：各层独立，修改影响范围小
3. **易于测试**：各层可独立测试
4. **易于扩展**：新增功能只需添加对应服务
5. **向后兼容**：所有现有代码无需修改

## ⚠️ 注意事项

- 旧的 `app.py` 和 `contact.py` 文件仍然存在，可以保留作为备份
- 如果使用 Gunicorn，启动命令改为：`gunicorn -w 4 -b 0.0.0.0:5000 main:app`
- 所有 API 端点路径和格式保持不变

## 🆘 问题排查

如果遇到导入错误，请确保：
1. 已安装所有依赖：`pip install -r requirements.txt`
2. 在 `flask_server` 目录下运行
3. Python 版本 >= 3.7


