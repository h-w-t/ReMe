#!/usr/bin/env python3
"""详细对比成功和失败的请求"""
import asyncio
import json
from openai import AsyncOpenAI

async def test_minimal():
    """最简单的成功测试"""
    print("=" * 60)
    print("1. 最简单的请求（已知成功）")
    print("=" * 60)
    
    client = AsyncOpenAI(
        api_key="sk-lm-e2e0PK8Q:mCXt3UaHAA2w9jOiI1Bc",
        base_url="http://localhost:1234/v1"
    )
    
    try:
        response = await client.chat.completions.create(
            model="qwen/qwen3-8b",
            messages=[{"role": "user", "content": "hi"}],
            stream=True
        )
        print("✅ 成功")
        async for chunk in response:
            pass  # 消费流
    except Exception as e:
        print(f"❌ 失败: {e}")

async def test_with_extra_params():
    """带额外参数的请求"""
    print("\n" + "=" * 60)
    print("2. 带额外参数的请求（temperature, max_tokens）")
    print("=" *60)
    
    client = AsyncOpenAI(
        api_key="sk-lm-e2e0PK8Q:mCXt3UaHAA2w9jOiI1Bc",
        base_url="http://localhost:1234/v1"
    )
    
    try:
        response = await client.chat.completions.create(
            model="qwen/qwen3-8b",
            messages=[{"role": "user", "content": "hi"}],
            stream=True,
            temperature=0.6,
            max_tokens=100
        )
        print("✅ 成功")
        async for chunk in response:
            pass
    except Exception as e:
        print(f"❌ 失败: {e}")

async def test_long_message():
    """较长的消息"""
    print("\n" + "=" * 60)
    print("3. 较长的消息内容")
    print("=" * 60)
    
    client = AsyncOpenAI(
        api_key="sk-lm-e2e0PK8Q:mCXt3UaHAA2w9jOiI1Bc",
        base_url="http://localhost:1234/v1"
    )
    
    long_content = """# Execution Process
### step.0 role=user content=
测试

### step.1 role=assistant content=
回复

Given the execution process above, please analyze it and extract: the task, solution, and key insights."""
    
    try:
        response = await client.chat.completions.create(
            model="qwen/qwen3-8b",
            messages=[{"role": "user", "content": long_content}],
            stream=True,
            temperature=0.6
        )
        print("✅ 成功")
        async for chunk in response:
            pass
    except Exception as e:
        print(f"❌ 失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        if hasattr(e, 'response'):
            print(f"   响应状态码: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")

async def main():
    await test_minimal()
    await asyncio.sleep(1)
    await test_with_extra_params()
    await asyncio.sleep(1)
    await test_long_message()

if __name__ == "__main__":
    asyncio.run(main())
