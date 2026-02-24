"""
Token Tracker — cross-process, sync+async OpenAI monkey-patch.

Usage in a run script
---------------------
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from token_tracker import patch_openai, patch_async_openai, start_periodic_logging

    patch_openai()           # intercept sync OpenAI chat.completions.create
    patch_async_openai()     # intercept async OpenAI chat.completions.create (HaluMem / ReMe-in-process)
    start_periodic_logging(interval=120, label="FrozenLake")   # print every 2 min

Usage in a Ray actor __init__
------------------------------
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from token_tracker import patch_openai, _append_usage      # noqa

    patch_openai()

Token log file
--------------
REME_TOKEN_LOG env var (absolute path) overrides default ./logs/token_usage.jsonl.
Set it in .env.cloud so all processes (ReMe service + agents) share one file.

    REME_TOKEN_LOG=/root/ReMe/logs/token_usage.jsonl
"""

from __future__ import annotations

import atexit
import copy
import fcntl
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path

from loguru import logger

# ─── Shared log file path ────────────────────────────────────────────────────
_LOG_ENV = os.getenv("REME_TOKEN_LOG")
TOKEN_LOG_PATH: Path = (
    Path(_LOG_ENV).expanduser().resolve()
    if _LOG_ENV
    else (Path("./logs/token_usage.jsonl")).resolve()
)

# ─── In-process counter (thread-safe) ────────────────────────────────────────
_lock = threading.Lock()
_counters: dict = {
    "calls": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "by_model": {},   # model_name → {calls, prompt, completion}
}
_start_time = time.time()

# ─── Patch guards ────────────────────────────────────────────────────────────
_sync_patched = False
_async_patched = False


# ─── Core accumulation ───────────────────────────────────────────────────────

def _append_usage(model: str, prompt: int, completion: int) -> None:
    """Record token usage in-process and persist to shared JSONL file."""
    if prompt == 0 and completion == 0:
        return
    # In-process
    with _lock:
        _counters["calls"] += 1
        _counters["prompt_tokens"] += prompt
        _counters["completion_tokens"] += completion
        m = _counters["by_model"].setdefault(
            model, {"calls": 0, "prompt": 0, "completion": 0}
        )
        m["calls"] += 1
        m["prompt"] += prompt
        m["completion"] += completion

    # Persist to shared file (cross-process)
    record = {
        "ts": time.time(),
        "pid": os.getpid(),
        "model": model,
        "prompt": prompt,
        "completion": completion,
    }
    try:
        TOKEN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_LOG_PATH, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(json.dumps(record) + "\n")
            fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as exc:
        logger.warning(f"[TokenTracker] failed to write log: {exc}")


def _extract_usage(usage_obj) -> tuple[int, int]:
    """Pull (prompt_tokens, completion_tokens) from a usage object."""
    if usage_obj is None:
        return 0, 0
    pt = getattr(usage_obj, "prompt_tokens", None) or 0
    ct = getattr(usage_obj, "completion_tokens", None) or 0
    return int(pt), int(ct)


# ─── Aggregation (reads shared file) ─────────────────────────────────────────

def aggregate_stats(since: float = 0.0) -> dict:
    """Read and sum all records from the shared JSONL log file."""
    stats: dict = {
        "calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "by_model": {},
    }
    if not TOKEN_LOG_PATH.exists():
        return stats
    try:
        with open(TOKEN_LOG_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("ts", 0) < since:
                    continue
                pt = int(r.get("prompt", 0))
                ct = int(r.get("completion", 0))
                stats["calls"] += 1
                stats["prompt_tokens"] += pt
                stats["completion_tokens"] += ct
                m = stats["by_model"].setdefault(
                    r.get("model", "unknown"),
                    {"calls": 0, "prompt": 0, "completion": 0},
                )
                m["calls"] += 1
                m["prompt"] += pt
                m["completion"] += ct
    except Exception as exc:
        logger.warning(f"[TokenTracker] failed to read log: {exc}")
    return stats


# ─── Pretty printer ──────────────────────────────────────────────────────────

def print_summary(prefix: str = "") -> None:
    """Print aggregated token statistics to console and logger."""
    s = aggregate_stats(since=_start_time)
    elapsed = time.time() - _start_time
    total = s["prompt_tokens"] + s["completion_tokens"]

    lines = [
        "=" * 66,
        f"[TokenTracker] {prefix}  elapsed={elapsed:.0f}s  calls={s['calls']}",
        f"  TOTAL : {total:>12,} tok  "
        f"(prompt={s['prompt_tokens']:,}  completion={s['completion_tokens']:,})",
    ]
    for mdl, m in sorted(s["by_model"].items()):
        mtotal = m["prompt"] + m["completion"]
        lines.append(
            f"  {mdl:<38s}  {mtotal:>10,} tok  ({m['calls']} calls)"
        )
    lines.append("=" * 66)
    msg = "\n".join(lines)
    print(msg, flush=True)
    logger.info(msg)


# ─── Background periodic logger ──────────────────────────────────────────────

def start_periodic_logging(interval: int = 120, label: str = "") -> None:
    """
    Start a daemon thread that prints token stats every *interval* seconds.
    Also registers a final summary at process exit via atexit.

    Args:
        interval: seconds between each periodic report (default 120)
        label:    short string shown in header (e.g. "FrozenLake")
    """
    atexit.register(print_summary, f"FINAL {'[' + label + ']' if label else ''}")

    def _loop() -> None:
        n = 0
        while True:
            time.sleep(interval)
            n += 1
            ts = datetime.now().strftime("%H:%M:%S")
            print_summary(f"periodic#{n} @ {ts} [{label}]")

    t = threading.Thread(target=_loop, daemon=True, name=f"token-tracker-{label}")
    t.start()
    logger.info(
        f"[TokenTracker] started — log={TOKEN_LOG_PATH}  interval={interval}s"
    )
    print(
        f"[TokenTracker] periodic token report every {interval}s "
        f"→ {TOKEN_LOG_PATH}",
        flush=True,
    )


# ─── Sync monkey-patch ───────────────────────────────────────────────────────

class _SyncStreamWrapper:
    """Wrap a sync OpenAI Stream to capture the usage chunk at end."""

    def __init__(self, stream, model: str):
        self._stream = stream
        self._model = model

    def __iter__(self):
        for chunk in self._stream:
            usage = getattr(chunk, "usage", None)
            if usage:
                pt, ct = _extract_usage(usage)
                if pt + ct > 0:
                    _append_usage(self._model, pt, ct)
            yield chunk

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if hasattr(self._stream, "__exit__"):
            return self._stream.__exit__(*args)

    def __getattr__(self, name: str):
        return getattr(self._stream, name)


def patch_openai() -> None:
    """
    Monkey-patch openai.resources.chat.completions.Completions.create
    to intercept all sync calls and record token usage.
    Safe to call multiple times (idempotent).
    """
    global _sync_patched
    if _sync_patched:
        return
    _sync_patched = True

    try:
        import openai.resources.chat.completions as _mod

        _orig = _mod.Completions.create

        def _patched(self_inner, *args, **kwargs):
            stream = kwargs.get("stream", False)
            model = kwargs.get("model", "unknown")
            if not stream:
                resp = _orig(self_inner, *args, **kwargs)
                usage = getattr(resp, "usage", None)
                if usage:
                    pt, ct = _extract_usage(usage)
                    _append_usage(model, pt, ct)
                return resp
            else:
                wrapped = _orig(self_inner, *args, **kwargs)
                return _SyncStreamWrapper(wrapped, model)

        _mod.Completions.create = _patched
        logger.info("[TokenTracker] sync OpenAI patched")
    except Exception as exc:
        logger.warning(f"[TokenTracker] failed to patch sync OpenAI: {exc}")


# ─── Async monkey-patch ───────────────────────────────────────────────────────

class _AsyncStreamWrapper:
    """Wrap an async OpenAI AsyncStream to capture the usage chunk at end."""

    def __init__(self, stream, model: str):
        self._stream = stream
        self._model = model

    def __aiter__(self):
        return self._iter()

    async def _iter(self):
        async for chunk in self._stream:
            usage = getattr(chunk, "usage", None)
            if usage:
                pt, ct = _extract_usage(usage)
                if pt + ct > 0:
                    _append_usage(self._model, pt, ct)
            yield chunk

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        if hasattr(self._stream, "__aexit__"):
            await self._stream.__aexit__(*args)

    def __getattr__(self, name: str):
        return getattr(self._stream, name)


def patch_async_openai() -> None:
    """
    Monkey-patch openai.resources.chat.completions.AsyncCompletions.create
    to intercept all async calls and record token usage.
    Must be called BEFORE any AsyncOpenAI client is created.
    Safe to call multiple times (idempotent).
    """
    global _async_patched
    if _async_patched:
        return
    _async_patched = True

    try:
        import openai.resources.chat.completions as _mod

        _orig_async = _mod.AsyncCompletions.create

        async def _patched_async(self_inner, *args, **kwargs):
            stream = kwargs.get("stream", False)
            model = kwargs.get("model", "unknown")
            if not stream:
                resp = await _orig_async(self_inner, *args, **kwargs)
                usage = getattr(resp, "usage", None)
                if usage:
                    pt, ct = _extract_usage(usage)
                    _append_usage(model, pt, ct)
                return resp
            else:
                wrapped = await _orig_async(self_inner, *args, **kwargs)
                return _AsyncStreamWrapper(wrapped, model)

        _mod.AsyncCompletions.create = _patched_async
        logger.info("[TokenTracker] async OpenAI patched")
    except Exception as exc:
        logger.warning(f"[TokenTracker] failed to patch async OpenAI: {exc}")
