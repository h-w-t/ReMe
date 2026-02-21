#!/usr/bin/env python3
"""直接测试 flowllm 的 OpenAICompatibleLLM 类"""
import asyncio
import sys
sys.path.insert(0, "/home/alex/wsl_projects/ReMe")

from flowllm.core.llm.openai_compatible_llm import OpenAICompatibleLLM
from flowllm.core.schema.message import Message

async def test_flowllm():
    print("=" * 60)
    print("测试 flowllm OpenAICompatibleLLM")
    print("=" * 60)
    
    llm = OpenAICompatibleLLM(
        base_url="http://localhost:1234/v1",
        api_key="sk-lm-e2e0PK8Q:mCXt3UaHAA2w9jOiI1Bc",
        model_name="qwen/qwen3-8b",
        temperature=0.6
    )
    
    messages = [Message(role="user", content="Hello, say hi back")]
    
    try:
        print("\n📤 发送请求...")
        response = await llm.achat(messages=messages)
        print(f"✅ 成功！响应: {response.content[:100]}...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_flowllm())
