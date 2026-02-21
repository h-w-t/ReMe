#!/usr/bin/env python3
"""测试 OpenAI 库与 LM Studio 的流式交互"""
import asyncio
from openai import AsyncOpenAI

async def test_stream():
    client = AsyncOpenAI(
        api_key="sk-lm-e2e0PK8Q:mCXt3UaHAA2w9jOiI1Bc",
        base_url="http://localhost:1234/v1"
    )
    
    print("=" * 60)
    print("测试流式聊天")
    print("=" * 60)
    
    try:
        stream = await client.chat.completions.create(
            model="qwen/qwen3-8b",
            messages=[{"role": "user", "content": "hello"}],
            stream=True
        )
        
        print("\n✅ 流式请求成功，接收响应：\n")
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n\n✅ 测试完成")
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stream())
