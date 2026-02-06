# ReMe 环境构建完成

## 🎉 安装摘要

使用 uv 工具已成功构建 ReMe 开发环境：

### ✅ 已安装组件

**核心包（可编辑模式）：**
- `reme-ai` 0.3.0.0a1 (可编辑)
- `reme` 0.3.0.0a1
- `flowllm` 0.2.0.10
- `sqlite-vec` 0.1.6

**实验依赖：**
- `gymnasium` 1.2.3 - FrozenLake 环境
- `ray` 2.53.0 - 并行执行
- `tabulate` 0.9.0 - 工具记忆
- `pandas` 2.3.3 - 数据分析
- `loguru` 0.7.3 - 日志
- `openai` 2.17.0 - LLM API
- `jinja2` 3.1.6 - 模板
- `python-dotenv` 1.2.1 - 环境变量
- `pyyaml` 6.0.3 - 配置文件

**Python 版本：** 3.10.12

---

## 🚀 快速开始

### 1. 激活环境

```bash
# 方式 1: 使用激活脚本（推荐）
source activate.sh

# 方式 2: 手动激活
export PATH="$HOME/.local/bin:$PATH"
source .venv/bin/activate
```

### 2. 配置 API Keys

编辑 `.env` 文件，填入你的 API 配置：

```bash
FLOW_EMBEDDING_API_KEY=sk-your-embedding-key
FLOW_EMBEDDING_BASE_URL=https://your-embedding-url/v1
FLOW_LLM_API_KEY=sk-your-llm-key
FLOW_LLM_BASE_URL=https://your-llm-url/v1
```

### 3. 验证安装

```bash
# 验证 Python 导入
python -c "from reme_ai import ReMeApp; print('ReMe 安装成功!')"

# 验证包版本
python -c "import reme_ai; print(f'reme_ai: {reme_ai.__version__}')"
python -c "import reme; print(f'reme: {reme.__version__}')"
```

---

## 🧪 运行实验

### Simple Demo（推荐首次体验）

```bash
cd cookbook/simple_demo
python import_usage_demo.py
```

### FrozenLake（轻量级实验）

```bash
cd cookbook/frozenlake
python run_frozenlake.py --help
python run_frozenlake.py  # 运行实验
python run_exp_statistic.py  # 统计结果
```

### Tool Memory

```bash
cd cookbook/tool_memory
# 参考目录中的 README 或脚本运行实验
```

### Working Memory

```bash
cd cookbook/working_memory
python work_memory_demo.py
```

---

## 🔧 独立环境说明

由于版本冲突，以下实验需要独立环境（未来云端配置）：

### AppWorld（Python 3.12 + pydantic 冲突）

```bash
uv venv --python 3.12 .venv-appworld
source .venv-appworld/bin/activate
uv pip install -e .
uv pip install -r cookbook/appworld/requirements.txt
uv pip install appworld
```

### BFCL（Python 3.12 + 需要 gorilla 仓库）

```bash
uv venv --python 3.12 .venv-bfcl
source .venv-bfcl/bin/activate

# 克隆并安装 BFCL 基准
cd ~
git clone https://github.com/ShishirPatil/gorilla.git
cd gorilla/berkeley-function-call-leaderboard
uv pip install -e .

# 返回 ReMe 目录安装
cd /home/alex/wsl_projects/ReMe
uv pip install -e .
uv pip install -r cookbook/bfcl/requirements.txt
```

---

## 📦 依赖管理

### 安装额外包

```bash
# 激活环境后
uv pip install <package-name>
```

### 查看已安装包

```bash
uv pip list
```

### 更新 ReMe（可编辑模式）

可编辑模式下，直接修改源代码即可生效，无需重新安装。

如需更新依赖：

```bash
uv pip install -e . --upgrade
```

---

## 🛠️ 工具说明

### uv 工具

- **速度快：** 比 pip 快 10-100 倍
- **可靠性：** 依赖解析更准确
- **兼容性：** 与 pip 命令相似

### 命令对照

| pip 命令 | uv 命令 |
|---------|---------|
| `pip install package` | `uv pip install package` |
| `pip uninstall package` | `uv pip uninstall package` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |

---

## 📝 开发提示

### 可编辑模式优势

当前 ReMe 以**可编辑模式**安装：
- ✅ 修改源码立即生效（无需重新安装）
- ✅ 方便调试和开发
- ✅ 适合实验研究
- ✅ 代码保持在项目目录，便于版本控制

### 目录结构

```
ReMe/
├── .venv/                # 虚拟环境（主环境）
├── .env                  # API 配置（需手动填写）
├── activate.sh           # 快速激活脚本
├── reme/                 # reme 核心代码（可编辑）
├── reme_ai/              # reme_ai 核心代码（可编辑）
└── cookbook/             # 实验代码
    ├── simple_demo/      # ✅ 简单示例
    ├── frozenlake/       # ✅ FrozenLake 实验
    ├── tool_memory/      # ✅ 工具记忆
    ├── working_memory/   # ✅ 工作记忆
    ├── appworld/         # ⚠️ 需要独立环境
    └── bfcl/             # ⚠️ 需要独立环境
```

---

## ❓ 故障排查

### 问题 1: uv 命令未找到

```bash
# 每次新终端需要添加 PATH
export PATH="$HOME/.local/bin:$PATH"

# 或添加到 ~/.bashrc 永久生效
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 问题 2: 导入 ReMe 失败

```bash
# 确保虚拟环境已激活
source .venv/bin/activate

# 检查安装状态
uv pip list | grep reme-ai
```

### 问题 3: API 配置错误

```bash
# 检查 .env 文件
cat .env

# 确保没有多余空格和引号
# 正确格式: FLOW_LLM_API_KEY=sk-xxxx
# 错误格式: FLOW_LLM_API_KEY = "sk-xxxx"
```

---

## 🌟 下一步

1. **配置 API Keys**：编辑 `.env` 文件
2. **运行 Simple Demo**：`cd cookbook/simple_demo && python import_usage_demo.py`
3. **探索实验**：查看 [docs/cookbook](docs/cookbook) 目录
4. **阅读文档**：访问 [ReMe 文档](https://reme.agentscope.io/)

---

## 📞 获取帮助

- **文档**: https://reme.agentscope.io/
- **GitHub**: https://github.com/agentscope-ai/ReMe
- **Issues**: https://github.com/agentscope-ai/ReMe/issues

祝实验顺利！🎉
