# Next Session: Cloud Deployment & Experiments

## 当前状态
- 分支 `experiment/cloud-ollama` 已推送到远程
- 本地 Phase 1-2 完成：simple_demo ✅，tool_memory (+16.75%) ✅
- 代码适配完成，准备在云端执行全部实验

---

## 架构速查

### 模型分工
| 实验 | 层级 | 模型 | 路由 |
|---|---|---|---|
| FrozenLake / BFCL / ToolMemory | agent executor + ReMe Ops | `qwen3:8b` | Ollama |
| HaluMem 底层 default LLM | `reme_model_name` | `google/gemini-2.5-flash` | OpenRouter |
| HaluMem QA 生成 + 评估 | `qwen3_max_instruct` | `qwen/qwen3-max` | OpenRouter |
| HaluMem 记忆推理 | `qwen-plus-thinking` | `qwen/qwen-plus-2025-07-28:thinking` | OpenRouter |
| Embedding（全部） | — | `text-embedding-qwen3-embedding-0.6b` | Ollama |

### VRAM（RTX 4090 24GB）
- Ollama 常驻：`qwen3:8b` (~5GB) + embed (~1GB) ≈ **6GB / 24GB**
- HaluMem 期间全部走 OpenRouter，Ollama 仅保留 embed

### 环境变量（`.env.cloud` 模板，已在本地，未入 git）
```dotenv
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
FLOW_LLM_API_KEY=ollama
FLOW_LLM_BASE_URL=http://localhost:11434/v1
FLOW_EMBEDDING_API_KEY=ollama
FLOW_EMBEDDING_BASE_URL=http://localhost:11434/v1
OPENROUTER_API_KEY=sk-or-xxxx          # ← 填入真实 key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

---

## Phase 4：云端部署步骤

### 1. 启动实例
- 平台：OpenBayes，选 **NVIDIA RTX 4090 24GB**（¥2.50/时，无时间限制）
- 镜像：Ollama 0.6.6

### 2. 环境准备
```bash
git clone https://github.com/h-w-t/ReMe.git
cd ReMe
git checkout experiment/cloud-ollama

# 配置环境变量（从本地上传或手动填写）
cp .env.cloud .env          # .env.cloud 需手动上传，因未入 git
# 编辑 .env，填入真实 OPENROUTER_API_KEY

source activate.sh          # 安装依赖
```

### 3. 拉取 Ollama 模型
```bash
ollama pull qwen3:8b
ollama pull qwen3:0.6b-embedding    # → text-embedding-qwen3-embedding-0.6b
# 注意：不需要 30b 模型（HaluMem 全走 OpenRouter）

# 验证
curl http://localhost:11434/v1/models
```

### 4. 启动 ReMe 服务
```bash
reme backend=http http.port=8002 config_path=cloud_ollama
# 健康检查
curl http://localhost:8002/health    # → {"status":"healthy"}
```

### 5. Stage 1：并行实验（tmux 两个窗口同时运行）

**窗口 A — FrozenLake**
```bash
tmux new-session -d -s frozenlake
tmux send-keys -t frozenlake "cd /root/ReMe/cookbook/frozenlake && python run_frozenlake.py" Enter
# 目标：pass rate ≥ 0.72（论文基线 0.66）
# 结果：cookbook/frozenlake/exp_result/
```

**窗口 B — BFCL-V3**
```bash
tmux new-window -t frozenlake -n bfcl
tmux send-keys -t frozenlake:bfcl "cd /root/ReMe/cookbook/bfcl" Enter
# 首次运行需额外准备：
python3.12 -m venv .venv-bfcl && source .venv-bfcl/bin/activate
pip install -r requirements.txt
python split_into_trainval.py
# 然后运行实验：
python run_bfcl.py
# 目标：Pass@4 ≥ 0.6577（论文基线 0.5955）
# 结果：cookbook/bfcl/exp_result/
```

### 6. Stage 2：顺序实验（等 Stage 1 完成后）

**Tool Memory**
```bash
cd /root/ReMe/cookbook/tool_memory
python run_reme_tool_bench.py
# 目标：avg_score 提升 ≥ +14.88%（本地实测 +16.75%）
```

**HaluMem**
```bash
cd /root/ReMe/benchmark/halumem

# 下载数据集（替换为实际 URL）
mkdir -p data
wget <HaluMem-Medium.jsonl-url> -O data/HaluMem-Medium.jsonl

# 小规模验证（2 用户）
python eval_reme.py --user_num 2 --max_concurrency 1

# 完整运行（默认参数即正确配置）
python eval_reme.py --user_num 100 --max_concurrency 3
# reme_model_name=google/gemini-2.5-flash（OR）
# eval_model_name=qwen/qwen3-max（OR）

# 查看结果
cat bench_results/reme/eval_statistics.json
```

### 7. ⚠️ 关闭实例
Stage 2 完成后立即关闭，预计总计 ≈ 4hr → **≈ ¥10**

---

## 结果收集路径
| 实验 | 结果目录 | 关键指标 |
|---|---|---|
| FrozenLake | `cookbook/frozenlake/exp_result/` | pass rate |
| BFCL-V3 | `cookbook/bfcl/exp_result/` | Pass@4, Avg@4 |
| Tool Memory | `cookbook/tool_memory/` | avg_score improvement |
| HaluMem | `benchmark/halumem/bench_results/reme/eval_statistics.json` | Correct Rate |

---

## 已知注意事项
1. **`.env.cloud` 未入 git**（含 API key），需从本地手动上传到云端实例
2. **BFCL 需要 Python 3.12 独立 venv**（`.venv-bfcl`），与主项目 venv 分开
3. FrozenLake 和 BFCL 使用不同 `workspace_id`，可安全共享同一 ReMe 服务
4. HaluMem `max_concurrency=3` 已在代码默认值中设置，无需额外参数
5. HaluMem 数据集 URL 需自行获取（论文仓库或作者联系）
