# ReMe 项目 LLM 接口调用逻辑梳理

> 整理时间：2026-02-27  
> 覆盖分支：`experiment/cloud-ollama`

本文梳理了 ReMe 项目中各实验模块对各类大模型接口的调用方式，分为三个层次：**Agent 推理层**（直接调用 LLM）、**ReMe 服务内部 LLM 配置**（记忆 Op 使用）、**记忆操作层**（间接通过 ReMe 服务调用 LLM）。

---

## 一、Agent 推理层（直接 LLM 调用）

各实验的 Agent 逻辑在推理步骤中直接调用 LLM，所用客户端及参数如下。

| 实验模块 | 入口文件 | LLM 调用方式 | 默认模型 | endpoint / base_url | 认证方式 | 特殊参数 |
|---|---|---|---|---|---|---|
| **HaluMem — 问答/评估** | `benchmark/halumem/eval_reme.py` | `reme.get_llm("qwen3_max_instruct").simple_request_for_json()` | `qwen3-max` | `BAILIAN_BASE_URL`（阿里云百炼） | `BAILIAN_API_KEY` | — |
| **BFCL — 工具调用** | `cookbook/bfcl/bfcl_agent.py` | `openai.OpenAI().chat.completions.create()` | `qwen3:8b`（Ollama） | `OPENAI_BASE_URL`，默认 `http://localhost:11434/v1` | `OPENAI_API_KEY`，默认 `"ollama"` | `tools=tool_schemas`，`parallel_tool_calls=True`；思考链通过系统消息前缀 `/think` 或 `/no_think` 控制 |
| **AppWorld — 任务执行** ⚠️ | `cookbook/appworld/appworld_react_agent.py` | `openai.OpenAI().chat.completions.create()` | `qwen3-8b` | 读取 `.env` 环境变量 | 读取 `.env` 环境变量 | `extra_body={"enable_thinking": False}`；**云端双后端配置待处理** |
| **FrozenLake — 游戏决策** | `cookbook/frozenlake/frozenlake_react_agent.py` | `openai.OpenAI().chat.completions.create()` | 小模型：`qwen3:8b`（Ollama）；大模型：`qwen3-max`（百炼） | 构造时传入 `llm_base_url`（默认 `http://localhost:11434/v1`）或 `BAILIAN_BASE_URL` | `llm_api_key`（Ollama 传 `"ollama"`，百炼传 `BAILIAN_API_KEY`） | 自动检测后端：Ollama 用 `/think` / `/no_think` 前缀；DashScope 用 `extra_body={"enable_thinking": ...}` |
| **Working Memory Demo** | `cookbook/working_memory/react_agent_with_working_memory.py` | `flowllm.OpenAICompatibleLLM` | 构造时传入 | 读取 `.env` 环境变量 | 读取 `.env` 环境变量 | 通过 FlowLLM 封装，标准 OpenAI-compatible 接口 |
| **Simple Demo** | `cookbook/simple_demo/` | 无直接 LLM 调用 | — | — | — | 全部通过 ReMe HTTP API 转发 |

### 关键说明

- **BFCL** 中，Ollama 不支持 DashScope 的 `extra_body={"enable_thinking": ...}` 参数，因此改用在系统消息开头注入 `/think\n` 或 `/no_think\n` 前缀来控制 Qwen3 的思考链行为（见 `_inject_thinking_prefix` 方法）。
- **AppWorld** 直接实例化 `openai.OpenAI()`，不传 `base_url` / `api_key`，依赖 `.env` 文件中的 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL`。**云端双后端配置尚未完成（待处理）**。
- **FrozenLake** 构造时接受显式 `llm_base_url` / `llm_api_key` / `enable_thinking` 参数，通过 `_is_ollama()` 自动判断后端类型：Ollama 实例将思考链前缀注入系统消息（`/think` or `/no_think`）；DashScope/百炼通过 `extra_body={"enable_thinking": ...}` 控制。`run_frozenlake.py` 的 `main()` 中提供了切换小模型（Ollama）和大模型（百炼）的注释模板。
- **HaluMem** 不直接使用 `openai` SDK，而是通过 `ReMe` Python SDK 的 `reme.get_llm(key)` 获取已配置的 LLM 实例，再调用 `simple_request_for_json()`。

---

## 二、ReMe 服务内部 LLM 配置（记忆 Ops 使用）

ReMe 服务通过配置文件管理 LLM，各实验启动服务时选择不同配置文件（`default.yaml` 或 `cloud_ollama.yaml`），内部 Op 根据 LLM key 路由到对应模型。

### 2.1 标准配置（`reme/config/default.yaml`）

适用于直连 DashScope / 阿里云百炼场景。

| LLM Key | backend | 实际模型 | 说明 |
|---|---|---|---|
| `default` | `openai` | `qwen3-30b-a3b-instruct-2507` | 所有内部 Op 默认使用 |
| `qwen3_8b_instruct` | `openai` | `qwen/qwen3-8b` | 轻量本地模型 |
| `qwen3_max_instruct` | `openai` | `qwen3-max` | HaluMem 问答与评估 |
| `qwen-plus-thinking` | `openai` | `qwen-plus-thinking-2025-01-21` | 思考链模式，`enable_thinking: True` |

### 2.2 云端 Ollama 配置（`reme_ai/config/cloud_ollama.yaml`）

适用于在 OpenBayes RTX 4090 上通过 Ollama 托管开源模型、HaluMem 部分模型仍走阿里云百炼的混合场景。

| LLM Key | backend | 实际模型 | base_url | 使用场景 |
|---|---|---|---|---|
| `default` | `openai_compatible` | `qwen3:8b` | `http://localhost:11434/v1` | FrozenLake / BFCL / ToolMemory 等所有内部 Op |
| `agent_8b` | `openai_compatible` | `qwen3:8b` | `http://localhost:11434/v1` | Agent Executor 显式引用别名 |
| `qwen3_30b_instruct` | `openai_compatible` | `qwen3:8b`（重定向） | `http://localhost:11434/v1` | 兼容硬编码了此 key 的 Op（如 `AgenticRetrieveOp`） |
| `qwen3_max_instruct` | `openai_compatible` | `qwen3-max` | `${BAILIAN_BASE_URL}` | HaluMem 问答 |
| `qwen-plus-thinking` | `openai_compatible` | `qwen-plus-thinking-2025-01-21` | `${BAILIAN_BASE_URL}` | HaluMem 记忆摘要/检索（思考模式） |

---

## 三、记忆操作层（各实验通过 ReMe 服务间接调用 LLM）

所有实验的记忆读写均不直接调用 LLM，而是通过调用 **ReMe HTTP REST API** 或 **MCP** 完成，再由 ReMe 服务内部路由到对应 LLM。

| 实验模块 | 记忆调用方式 | ReMe 服务地址 | 涉及的 Flow |
|---|---|---|---|
| **HaluMem** | `reme.summarize_memory()` / `reme.retrieve_memory()`（Python SDK，内嵌 ReMe，无 HTTP） | 直接调用 | 个人记忆摘要 / 检索 |
| **BFCL** | `requests.post()` | `http://0.0.0.0:8002/` | `retrieve_task_memory`、`summary_task_memory` |
| **AppWorld** | `requests.post()` | `http://0.0.0.0:8002/` | `retrieve_task_memory`、`summary_task_memory` |
| **FrozenLake** | `requests.post()` | `http://0.0.0.0:8002/` | `retrieve_task_memory`、`summary_task_memory` |
| **Working Memory** | MCP tools + HTTP flow | MCP: `http://0.0.0.0:8002/sse`；HTTP: `http://localhost:8003` | `summary_working_memory`、`grep_working_memory`、`read_working_memory` |
| **Simple Demo** | `requests.post()` | `http://0.0.0.0:8002/` | `retrieve_task_memory`、`summary_task_memory` |

---

## 四、Embedding 模型配置

| 配置文件 | backend | 模型 | base_url |
|---|---|---|---|
| `reme/config/default.yaml` | `openai` | `text-embedding-qwen3-embedding-0.6b` | DashScope（默认） |
| `reme_ai/config/cloud_ollama.yaml` | `openai_compatible` | `text-embedding-qwen3-embedding-0.6b` | `http://localhost:11434/v1`（Ollama） |

两套配置所用模型相同，区别仅在于 endpoint：标准配置走 DashScope，云端配置走本地 Ollama。

---

## 五、Token 追踪机制

所有实验使用统一的 Token 追踪工具 `cookbook/token_tracker.py`，通过 **monkey-patch** `openai.resources.chat.completions.Completions.create`（同步）和 `AsyncCompletions.create`（异步）来拦截所有 OpenAI-compatible 调用，自动记录各模型的 `prompt_tokens` 和 `completion_tokens`。

- 每个 **Ray actor** 在初始化时各自调用 `patch_openai()` / `patch_async_openai()`，调用是幂等的（多次调用不会重复注入）。
- HaluMem `eval_reme.py` 在进程入口处统一调用，覆盖直接 LLM 调用和 ReMe 内部调用。

---

## 六、整体架构图

```
┌──────────────────────────────────────────────────────────┐
│                      实验 Agent 层                        │
│  BFCL / AppWorld / FrozenLake         HaluMem             │
│  openai.OpenAI() ──────────────────── reme.get_llm()      │
│  (Ollama / DashScope via .env)         (百炼 via ReMe SDK) │
└──────────────┬───────────────────────────────────────────┘
               │ 记忆读写（HTTP REST / MCP）
               ▼
┌──────────────────────────────────────────────────────────┐
│                    ReMe 服务层 (:8002)                    │
│  Flow: retrieve_task_memory / summary_task_memory / ...   │
│  LLM 路由 ──── default.yaml 或 cloud_ollama.yaml          │
└──────────────┬───────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
  Ollama :11434     阿里云百炼 DashScope
  (qwen3:8b,         (qwen3-max,
   embedding)         qwen-plus-thinking)
```

---

## 七、快速对照：各实验 LLM 使用汇总

| 实验 | Agent 推理模型 | 记忆 Op 默认模型 | 接口规范 | 思考链支持 |
|---|---|---|---|---|
| HaluMem | qwen3-max（百炼） | qwen-flash / qwen-plus-thinking（百炼） | OpenAI-compatible | 是（`enable_thinking` via `extra_body`） |
| BFCL | qwen3:8b（Ollama） | qwen3:8b（Ollama） | OpenAI-compatible | 是（系统消息前缀 `/think`） |
| **AppWorld** ⚠️ | qwen3-8b（DashScope/env）— **云端配置待处理** | qwen3:8b（Ollama 或 DashScope） | OpenAI-compatible | 否（`enable_thinking: False`） |
| **FrozenLake** | 小：qwen3:8b（Ollama）/ 大：qwen3-max（百炼） | qwen3:8b（Ollama 或 DashScope） | OpenAI-compatible | 是（自动适配：Ollama 前缀 / 百炼 extra_body） |
| Working Memory Demo | 构造时传入 | — | OpenAI-compatible（FlowLLM） | 取决于模型 |
| Simple Demo | — | ReMe 服务默认 | HTTP REST | 取决于服务配置 |
