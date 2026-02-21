#!/usr/bin/env python3
"""测试 ReMeApp 实际的 LLM 初始化方式"""
import asyncio
import os
from reme_ai.main import ReMeApp

async def test_with_reme_config():
    print("=" * 60)
    print("测试通过 ReMeApp 配置的 LLM")
    print("=" * 60)
    
    # 显示环境变量
    print("\n📋 环境变量:")
    print(f"   NO_PROXY: {os.getenv('NO_PROXY', 'not set')}")
    print(f"   no_proxy: {os.getenv('no_proxy', 'not set')}")
    print(f"   HTTP_PROXY: {os.getenv('HTTP_PROXY', 'not set')}")
    print(f"   HTTPS_PROXY: {os.getenv('HTTPS_PROXY', 'not set')}")
    
    async with ReMeApp(
        "llm.default.backend=openai_compatible",
        "llm.default.base_url=http://localhost:1234/v1",
        "llm.default.api_key=sk-lm-e2e0PK8Q:mCXt3UaHAA2w9jOiI1Bc",
        "llm.default.model_name=qwen/qwen3-8b",
        "llm.default.params.temperature=0.6",
        "vector_store.default.backend=memory",
    ) as app:
        print("\n✅ ReMeApp 初始化成功")
        
        # 使用最简单的流程测试 - 直接用 summary_task_memory_simple
        try:
            print("\n📤 测试简单任务记忆流程...")
            result = await app.async_execute(
                name="summary_task_memory_simple",
                workspace_id="test_workspace",
                trajectories=[{
                    "messages": [
                        {"role": "user", "content": "测试"},
                        {"role": "assistant", "content": "回复"}
                    ],
                    "score": 1.0
                }]
            )
            print(f"✅ 成功！结果: {result}")
            return True
            
        except Exception as e:
            print(f"❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = asyncio.run(test_with_reme_config())
    exit(0 if success else 1)
