# LM Studio API Token 配置指南

## 问题说明

LM Studio 启用了 API Token 认证，需要在请求时提供有效的 token。

错误信息示例：
```
401 Unauthorized
An LM Studio API token is required to make requests to this server
```

---

## 获取 API Token

### 方法 1: 从 LM Studio UI 获取

1. **打开 LM Studio**（在 Windows 上）

2. **进入 Local Server 标签**
   - 点击左侧导航栏的 "Local Server" 或 "Developer" 图标

3. **查找 API Token**
   - 在 Server 设置页面查找 "Authentication" 或 "API Token" 部分
   - 可能显示为 "API Key" 或 "Bearer Token"
   - 点击 "Show Token" 或 "Copy Token"

4. **复制 Token**
   - Token 格式通常类似: `lms-xxxxxxxxxxxxxxxxxxxxxxxx`
   - 或者是一串随机字符

### 方法 2: 从配置文件获取

LM Studio 可能将 token 保存在配置文件中（Windows 路径）：
```
C:\Users\<用户名>\.lmstudio\config.json
```

### 方法 3: 禁用认证（不推荐用于生产）

如果只是本地测试，可以在 LM Studio 设置中：
1. 进入 Local Server 设置
2. 查找 "Authentication" 或"Require API Token"
3. 关闭认证选项（如果可用）

---

## 配置 API Token

### 临时设置（仅当前会话）

```bash
# 导出环境变量
export LM_STUDIO_API_KEY='lms-your-token-here'

# 运行测试
python scripts/test_lm_studio.py
```

### 永久设置（推荐）

#### 选项 1: 添加到 .env 文件

编辑 `/home/alex/wsl_projects/ReMe/.env`，添加：

```bash
# LM Studio API Token
LM_STUDIO_API_KEY=lms-your-token-here

# 或者使用相同的 token 作为 API key
FLOW_LOCAL_LLM_API_KEY=lms-your-token-here
FLOW_LOCAL_EMBEDDING_API_KEY=lms-your-token-here
```

#### 选项 2: 添加到 shell 配置

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
# LM Studio 配置
export LM_STUDIO_API_KEY='lms-your-token-here'
```

然后重新加载：
```bash
source ~/.bashrc
```

---

## 测试连接

### 使用环境变量测试

```bash
# 设置 token
export LM_STUDIO_API_KEY='your-token-here'

# 运行测试
python scripts/test_lm_studio.py
```

### 使用 curl 测试

```bash
# 测试模型列表
curl -H "Authorization: Bearer lms-your-token-here" \
     http://localhost:1234/v1/models

# 测试推理
curl -H "Authorization: Bearer lms-your-token-here" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "local-model",
       "messages": [{"role": "user", "content": "你好"}],
       "max_tokens": 50
     }' \
     http://localhost:1234/v1/chat/completions
```

---

## 更新配置文件

### 更新 .env

```bash
# ========================================
# LM Studio 本地配置（轻量级任务使用）
# ========================================
LM_STUDIO_API_KEY=lms-your-actual-token-here
FLOW_LOCAL_LLM_BASE_URL=http://localhost:1234/v1
FLOW_LOCAL_LLM_API_KEY=${LM_STUDIO_API_KEY}
FLOW_LOCAL_EMBEDDING_BASE_URL=http://localhost:1234/v1
FLOW_LOCAL_EMBEDDING_API_KEY=${LM_STUDIO_API_KEY}
```

### 更新 reme_ai/config/default.yaml

```yaml
llm:
  local:
    backend: openai_compatible
    base_url: http://localhost:1234/v1
    api_key: ${LM_STUDIO_API_KEY}  # 从环境变量读取
    model_name: local-model
    params:
      temperature: 0.6

embedding_model:
  local:
    backend: openai_compatible
    base_url: http://localhost:1234/v1
    api_key: ${LM_STUDIO_API_KEY}  # 从环境变量读取
    model_name: text-embedding-qwen3-embedding-4b
```

---

## 故障排查

### 问题 1: Token 从哪里获取？

**解决方案：**
1. 检查 LM Studio 的 Local Server 界面
2. 查看是否有 "Settings" 或 "Authentication" 部分
3. 如果找不到，尝试更新 LM Studio 到最新版本

### 问题 2: 设置了 Token 仍然 401

**检查：**
```bash
# 确认环境变量已设置
echo $LM_STUDIO_API_KEY

# 确认 token 格式正确（无空格、换行）
export LM_STUDIO_API_KEY='lms-xxxxx'  # 使用单引号

# 测试
curl -H "Authorization: Bearer $LM_STUDIO_API_KEY" \
     http://localhost:1234/v1/models
```

### 问题 3: 不想使用认证

如果 LM Studio 允许，可以在设置中禁用认证：
1. LM Studio → Local Server → Settings
2. 查找 "Require Authentication" 或类似选项
3. 关闭该选项
4. 重启 Local Server

---

## 快速开始命令

```bash
# 1. 获取你的 LM Studio API Token（从 LM Studio UI）

# 2. 设置环境变量
export LM_STUDIO_API_KEY='lms-your-token-here'

# 3. 添加到 .env 文件（永久保存）
echo "LM_STUDIO_API_KEY=lms-your-token-here" >> .env

# 4. 运行测试
source activate.sh
python scripts/test_lm_studio.py

# 5. 如果测试通过，开始使用
python cookbook/simple_demo/import_usage_demo.py
```

---

## 参考资源

- LM Studio 官方文档: https://lmstudio.ai/docs
- API 认证文档: https://lmstudio.ai/docs/developer/core/authentication
- 问题反馈: https://github.com/lmstudio-ai/lmstudio.js/issues
