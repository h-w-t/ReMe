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

- [ ] **Start & Verify ReMe Service**
    - [ ] Start service: `reme backend=http http.port=8002`
    - [ ] Health check: `curl http://localhost:8002/`

## Phase 2: Local Small-Scale Verification (Priority: High)
*Goal: Ensure configuration is correct before migrating.*

- [ ] **Simple Demo Experiment**
    - [ ] Run `cookbook/simple_demo/test_local_model.py`.
    - [ ] Run `cookbook/simple_demo/import_usage_demo.py`.
    - [ ] Verify Personal/Task/Tool memory operations.

- [ ] **Tool Memory Experiment**
    - [ ] Run `cookbook/tool_memory/run_reme_tool_bench.py`.
    - [ ] Verify execution completes and results are generated.
    - [ ] Target Benchmark: ~14.88% improvement.

## Phase 3: Cloud Migration Preparation (Priority: Medium)
*Goal: Package code and scripts for cloud deployment.*

- [ ] **Code Portability**
    - [ ] Replace hardcoded paths with relative paths in experiment scripts:
        - [ ] `cookbook/appworld/run_appworld.py`
        - [ ] `cookbook/bfcl/bfcl_agent.py`
    - [ ] Standardize output directories (e.g., `./results/`).

- [ ] **Cloud Configuration Assets**
    - [ ] Create `.env.cloud` template (using env var injection).
    - [ ] Create `cloud_config.yaml` if needed.
    - [ ] Prepare Dockerfile or setup script (`activate.sh` usage).

- [ ] **Logging & Monitoring**
    - [ ] Configure file-based logging (Loguru).
    - [ ] Ensure results are saved to persistent paths.

## Phase 4: Cloud Deployment & Large-Scale Experiments (Priority: Medium)
*Goal: Run resource-intensive local/cloud hybrid experiments.*

- [ ] **Environment Setup on Cloud**
    - [ ] Upload codebase.
    - [ ] Install dependencies (`pip install -e .`).
    - [ ] Start ReMe service in background.

- [ ] **Run FrozenLake Experiment**
    - [ ] Script: `cookbook/frozenlake/run_frozenlake.py`
    - [ ] Config: `max_workers=4` (adjust based on cloud resources).
    - [ ] Result: Check pass rate improvement.

- [ ] **Run Working Memory Experiment**
    - [ ] Script: `cookbook/working_memory/work_memory_demo.py`
    - [ ] Config: Use Cloud LLM (Qwen-Max/GPT-4o) or Local 14B if available.

- [ ] **Run BFCL-V3 Experiment** (Complex)
    - [ ] Clone Gorilla repo & install `berkeley-function-call-leaderboard`.
    - [ ] Prepare data: `split_into_trainval.py`.
    - [ ] Run: `cookbook/bfcl/run_bfcl.py`.

- [ ] **Run Appworld Experiment** (Most Complex)
    - [ ] Create isolated Python 3.12 environment (if possible on cloud).
    - [ ] Install `appworld` and download data.
    - [ ] Run: `cookbook/appworld/run_appworld.py`.

## Phase 5: Analysis & Reporting
- [ ] **Data Collection**
    - [ ] Aggregate logs and result CSVs.
- [ ] **Performance Review**
    - [ ] Compare Local vs Cloud results.
    - [ ] Document pass rates and improvements.
