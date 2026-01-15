# 问题排查指南

## 问题：手机APP无法获取GUI1.py的数据

### 可能的原因和解决方案

### 1. ✅ 已修复：DetectionType 枚举缺少类型值

**问题**：PIVdata2.py 发送的类型值（如 `b2_mill_change`, `load_monitor`, `mill134_change`）不在枚举中，导致创建检测数据失败。

**修复**：已在 `domain/value_objects.py` 中添加所有类型值：
- `MILL134_CHANGE = "mill134_change"`
- `B2_MILL_CHANGE = "b2_mill_change"`
- `LOAD_MONITOR = "load_monitor"`

### 2. ⚠️ 检查：服务器是否使用新代码启动

**问题**：如果服务器仍在使用旧的 `app.py`，新代码的修复不会生效。

**解决方案**：

#### 方式1：使用新的 main.py 启动（推荐）
```bash
cd flask_server
python main.py
```

#### 方式2：如果使用 Gunicorn
```bash
# 旧命令（使用 app.py）
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 新命令（使用 main.py）
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

#### 方式3：如果使用 systemd 或其他服务管理
修改服务配置文件，将启动命令从 `app:app` 改为 `main:app`

### 3. 🔍 验证步骤

#### 步骤1：检查服务器是否运行
```bash
# 检查端口 5000 是否被占用
netstat -ano | findstr :5000  # Windows
# 或
lsof -i :5000  # Linux/Mac
```

#### 步骤2：测试 API 端点
```bash
# 测试健康检查
curl http://localhost:5000/health

# 测试接收数据
curl -X POST http://localhost:5000/receive_detection \
  -H "Content-Type: application/json" \
  -d '{"title":"测试","message":"测试消息","type":"b2_mill_change"}'

# 测试获取数据
curl http://localhost:5000/get_detections?type=all&limit=10
```

#### 步骤3：检查服务器日志
查看服务器控制台输出，确认：
- ✅ 数据接收成功：`📨 收到检测数据: ...`
- ❌ 如果有错误：`❌ 处理检测数据失败: ...`

### 4. 🐛 常见错误

#### 错误1：`ValueError: 'xxx' is not a valid DetectionType`
**原因**：类型值不在枚举中（已修复）

#### 错误2：`ModuleNotFoundError: No module named 'interface'`
**原因**：不在正确的目录下运行，或 Python 路径问题
**解决**：确保在 `flask_server` 目录下运行，或使用绝对路径

#### 错误3：数据接收成功但APP获取不到
**检查**：
1. 数据是否真的保存了（检查 `/get_detections` 返回）
2. APP 的 URL 是否正确
3. 网络连接是否正常

### 5. 📝 调试技巧

#### 启用详细日志
在 `interface/api.py` 中添加更多日志：

```python
@app.route('/receive_detection', methods=['POST'])
def receive_detection():
    try:
        data = request.get_json()
        print(f"🔍 收到数据: {data}")  # 添加这行
        # ... 其他代码
```

#### 检查数据存储
在 `application/detection_service.py` 中添加日志：

```python
def receive_detection(...):
    # ... 创建检测
    saved_detection = self.repository.add(detection)
    print(f"🔍 保存的数据ID: {saved_detection.id}")  # 添加这行
    print(f"🔍 仓库总数: {self.repository.count_total()}")  # 添加这行
```

### 6. ✅ 快速修复检查清单

- [ ] 确保服务器使用 `python main.py` 或 `gunicorn main:app` 启动
- [ ] 检查服务器日志，确认数据接收成功
- [ ] 测试 `/get_detections` 端点，确认数据可以获取
- [ ] 检查 APP 的 Flask 服务器地址配置是否正确
- [ ] 确认网络连接正常（APP 可以访问服务器）

### 7. 🆘 如果问题仍然存在

1. **重启服务器**：
   ```bash
   # 停止旧进程
   # Windows: 在任务管理器中结束 Python 进程
   # Linux: killall python 或 kill <PID>
   
   # 启动新进程
   cd flask_server
   python main.py
   ```

2. **清除缓存**：
   ```bash
   # 删除 Python 缓存
   find flask_server -name "*.pyc" -delete
   find flask_server -name "__pycache__" -type d -exec rm -r {} +
   ```

3. **检查依赖**：
   ```bash
   pip install -r requirements.txt
   ```

4. **查看完整错误日志**：
   检查服务器控制台的完整错误信息，特别是堆栈跟踪



