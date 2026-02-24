# ReMe Reproducibility Task List

This document outlines the roadmap for reproducing ReMe cookbook experiments, starting with environment setup and local verification, followed by migration to a cloud platform for large-scale experiments.

## Phase 1: Environment Configuration & Fixes (Priority: High)
- [x] **Verify .env Configuration**
    - [x] Ensure `OPENAI_API_KEY` & `OPENAI_BASE_URL` point to the desired Agent Executor (Local LM Studio or Cloud).
    - [x] Ensure `FLOW_LLM_API_KEY` & `FLOW_EMBEDDING_API_KEY` are set for ReMe Service.
    - [x] Verify connection to Local LM Studio (`http://localhost:1234/v1`).
    - [x] Verify connection to Cloud APIs (if configured).

- [x] **Fix Embedding Configuration** (`reme/config/default.yaml`)
    - [x] Change `dimensions` to `1024` (if using local `text-embedding-qwen3-embedding-0.6b`).
    - [x] Set `embedding_model.default.model_name` correctly.

- [x] **Fix Vector Store Configuration** (`reme/config/default.yaml`)
    - [x] Change `vector_store.default.backend` to `local` (SQLite) for easier migration.
    - [x] Ensure persistence paths are configured if needed.

- [x] **Start & Verify ReMe Service**
    - [x] Start service: `reme backend=http http.port=8002`
    - [x] Health check: `curl http://localhost:8002/health` → `{"status":"healthy"}`

## Phase 2: Local Small-Scale Verification (Priority: High)
*Goal: Ensure configuration is correct before migrating.*

- [x] **Simple Demo Experiment**
    - [x] Run `cookbook/simple_demo/test_local_model.py`. ✅ 任务记忆 + 个人记忆全部通过（LLM: OpenRouter `qwen/qwen3-30b-a3b-instruct-2507`，Embedding: 本地 LM Studio `text-embedding-qwen3-embedding-0.6b`）。
    - [x] Run `cookbook/simple_demo/import_usage_demo.py`. （待用修正后配置重跑）
    - [x] Verify Personal/Task/Tool memory operations. ✅ 通过。
    - **修复记录**：① `FLOW_LLM_BASE_URL` 从 `docs.newapi.pro`（307重定向→405）改为 OpenRouter；② `reme_ai` 模型名加 `qwen/` 前缀；③ Embedding 统一本地 LM Studio。

- [ ] **Tool Memory Experiment**
    - [x] Run `cookbook/tool_memory/run_reme_tool_bench.py`.
    - [x] Verify execution completes and results are generated.
    - [x] Target Benchmark: ~14.88% improvement. ✅ **实测 Epoch 1: +16.75% ↑**（Test 无记忆 avg_score=0.400 → 有记忆 avg_score=0.467）。
    - **修复记录**：① `SearchToolA/B/C` 类名不符合 flowllm 框架"必须以 `Op` 结尾"的要求，重命名为 `SearchToolAOp/BOp/COp`，并同步更新 `mock_search_tools.py`、`use_mock_search_op.py`、`__init__.py`。

## Phase 3: Cloud Migration Preparation (Priority: High)
*Goal: Adapt code for OpenBayes A6000 + Ollama, managed under `experiment/cloud-ollama` branch.*

### Model Architecture (Final)
| Role | Paper Model | Cloud Deployment | Backend |
|------|-------------|-----------------|---------|
| FrozenLake / BFCL / ToolMemory agent executor | qwen3-8b | `qwen3:8b` | Ollama |
| ReMe internal Ops (FrozenLake/BFCL/ToolMemory) | qwen3-8b | `qwen3:8b` | Ollama |
| HaluMem memory ops (thinking) | qwen-plus + enable_thinking | `qwen/qwen-plus-2025-07-28:thinking` | OpenRouter |
| HaluMem answer generation | qwen3-max | `qwen/qwen3-max` | OpenRouter |
| HaluMem QA evaluation | qwen3-max | `qwen/qwen3-max` | OpenRouter |
| HaluMem底层 default LLM | gemini-2.5-flash | `google/gemini-2.5-flash` | OpenRouter |
| Embedding (all) | text-embedding-qwen3-embedding-0.6b | same | Ollama |

> **RTX 4090 24GB** (¥2.50/时): Ollama 仅需 qwen3:8b (~5GB) + embed (~1GB) ≈ **6GB**，HaluMem 全部走 OpenRouter。总费用 ≈ ¥10（4hr）。

### Parallelism Strategy
- **Stage 1 (parallel):** FrozenLake + BFCL run simultaneously in two tmux windows (each `max_workers=4`, shared ReMe service via different `workspace_id`)
- **Stage 2 (sequential):** Tool Memory → HaluMem (`max_concurrency=3`), both heavy on `qwen3:30b`

- [x] **Create Branch** `experiment/cloud-ollama` for all cloud adaptations; `main` remains clean.

- [x] **Fix Hardcoded Paths** (`benchmark/halumem/eval_reme.py`)
    - [x] Changed `--data_path` default from `/Users/zhouwk/...` to `./data/HaluMem-Medium.jsonl`.

- [x] **Create `.env.cloud`**
    - [x] `OPENAI_*` → Ollama (agent executor layer)
    - [x] `FLOW_LLM_*` → Ollama (ReMe internal layer)
    - [x] `FLOW_EMBEDDING_*` → Ollama
    - [x] `OPENROUTER_*` → OpenRouter (HaluMem `qwen-plus-thinking` only)

- [x] **Create `reme_ai/config/cloud_ollama.yaml`**
    - [x] `llm.default` → `qwen3:30b-a3b-instruct-q8_0` via Ollama
    - [x] `llm.agent_8b` → `qwen3:8b` via Ollama
    - [x] `llm.qwen-plus-thinking` → OpenRouter (key aligned with `reme/config/default.yaml`)
    - [x] `embedding_model.default` → `text-embedding-qwen3-embedding-0.6b` via Ollama
    - [x] `vector_store.default.backend` → `local`

- [x] **Adapt BFCL `call_llm()` for Ollama** (`cookbook/bfcl/bfcl_agent.py`)
    - [x] Removed DashScope-specific `extra_body={"enable_thinking": ...}` and `stream=enable_thinking`.
    - [x] Added `_inject_thinking_prefix()`: injects `/think` or `/no_think` into system message (Ollama Qwen3 official control).
    - [x] `OpenAI` client now reads `OPENAI_BASE_URL` from env (points to Ollama).

- [x] **Fix HaluMem `qwen-plus-t` → `qwen-plus-thinking`** (`benchmark/halumem/eval_reme.py`)
    - [x] Renamed key `qwen-plus-t` → `qwen-plus-thinking` (aligned with `reme/config/default.yaml`).
    - [x] Updated model name `qwen-plus` → `qwen/qwen-plus-2025-07-28:thinking`.
    - [x] Added `base_url`/`api_key` from `OPENROUTER_*` env vars for this llm entry.
    - [x] Both `llm_config_name` references updated.
    - [x] Default `reme_model_name` → `qwen3:8b`, `eval_model_name` → `qwen3:30b-a3b-instruct-q8_0`, `max_concurrency` → `3`.

- [x] **Logging & Monitoring**
    - [x] Verify Loguru file sink configured (output to `./logs/`). ✅ `init_logger()` called from `service_context.py`，logs/ 目录已有历史日志文件。
    - [x] Ensure all result files are written to persistent `./exp_result/` or `./bench_results/`. ✅ 所有 run_*.py 均使用 `Path.mkdir(parents=True, exist_ok=True)` 自动创建。

## Phase 4: Cloud Deployment & Large-Scale Experiments (Priority: High)
*Goal: Run all experiments on OpenBayes A6000 48GB with Ollama.*

- [ ] **Cloud Environment Setup**
    - [ ] Launch OpenBayes **RTX 4090 24GB** instance with **Ollama 0.6.6** image（¥2.50/时，无时间限制）。
    - [ ] `git clone` repo and `git checkout experiment/cloud-ollama`.
    - [ ] `cp .env.cloud .env` and fill in `OPENROUTER_API_KEY`.
    - [ ] `source activate.sh` — install dependencies.
    - [ ] Pull models:
        ```bash
        ollama pull qwen3:8b
        ollama pull qwen3:0.6b-embedding   # text-embedding-qwen3-embedding-0.6b
        # Note: qwen3:30b NOT needed — HaluMem LLMs all via OpenRouter
        ```
    - [ ] Verify: `curl http://localhost:11434/v1/models` shows all 3 models.
    - [ ] Start ReMe service:
        ```bash
        reme backend=http http.port=8002 config_path=cloud_ollama
        ```
    - [ ] Health check: `curl http://localhost:8002/health` → `{"status":"healthy"}`.

- [ ] **Stage 1 — Parallel Experiments (Agent = qwen3:8b)**

    - [ ] **FrozenLake** (`cookbook/frozenlake/run_frozenlake.py`)
        - [ ] `tmux new-window`, `cd cookbook/frozenlake`.
        - [ ] Config: `model_name="qwen3:8b"`, `max_workers=4`, 50 training maps + 100 test maps, `is_slippery=False`.
        - [ ] Target: pass rate ≥ **0.72** (paper baseline 0.66 → +6%).
        - [ ] Results saved to `cookbook/frozenlake/exp_result/`.

    - [ ] **BFCL-V3** (`cookbook/bfcl/run_bfcl.py`)
        - [ ] Create `.venv-bfcl` (Python 3.12): `python3.12 -m venv .venv-bfcl && source .venv-bfcl/bin/activate`.
        - [ ] Clone gorilla repo & install: `pip install -r cookbook/bfcl/requirements.txt`.
        - [ ] Prepare data: `python split_into_trainval.py`.
        - [ ] Config: `model_name="qwen3:8b"`, `enable_thinking=True` (Ollama `/think` prefix), `max_workers=4`, `memory_base_url="http://0.0.0.0:8002/"`.
        - [ ] Run 50 train + 150 val tasks.
        - [ ] Target: Pass@4 ≥ **0.6577** (paper baseline 0.5955 → +6.22%).
        - [ ] Results saved to `cookbook/bfcl/exp_result/`.

- [ ] **Stage 2 — Sequential Experiments (ReMe heavy, qwen3:30b)**

    - [ ] **Tool Memory** (`cookbook/tool_memory/run_reme_tool_bench.py`)
        - [ ] ReMe service already running with `qwen3:30b` as default.
        - [ ] Run benchmark; verify LLM calls route to Ollama.
        - [ ] Target: Test avg_score improvement ≥ **+14.88%** (paper); local result was +16.75%.
        - [ ] Results saved to `cookbook/tool_memory/`.

    - [ ] **HaluMem** (`benchmark/halumem/eval_reme.py`)
        - [ ] Download dataset: `mkdir -p benchmark/halumem/data && wget <HaluMem-Medium.jsonl-url> -O benchmark/halumem/data/HaluMem-Medium.jsonl`.
        - [ ] Small-scale verify: `python eval_reme.py --user_num 2 --max_concurrency 1`.
        - [ ] Full run: `python eval_reme.py --user_num 100 --max_concurrency 3`（默认：`reme_model_name=google/gemini-2.5-flash`，`eval_model_name=qwen/qwen3-max`，均走 OR）。
        - [ ] Model routing check: `qwen-plus-thinking` → OpenRouter, all others → Ollama.
        - [ ] Collect results: `bash benchmark/halumem/scripts.sh` → Correct Rate output.

    - [ ] **⚠️ Shut down cloud instance immediately after Stage 2 completes.**
        - [ ] Estimated total: Stage 1 ≈ 1.5hr + Stage 2 ≈ 3hr → **≈ ¥10** (RTX 4090 ¥2.50/hr)。

## Phase 5: Analysis & Reporting
- [ ] **Data Collection**
    - [ ] Aggregate all results to `results/` directory:
        - `cookbook/frozenlake/exp_result/` → FrozenLake pass rates
        - `cookbook/bfcl/exp_result/` → BFCL Avg@4 / Pass@4
        - `cookbook/tool_memory/` → avg_score improvement
        - `benchmark/halumem/bench_results/` → HaluMem Correct Rate
- [ ] **Performance Review**
    - [ ] Compare results against README paper baselines.
    - [ ] Document all improvements with actual vs. expected values.
- [ ] **Branch Merge** (optional)
    - [ ] Review `experiment/cloud-ollama` diff vs `main`.
    - [ ] Merge adapted code back to `main` if changes are generalizable.

