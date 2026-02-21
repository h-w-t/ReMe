#!/usr/bin/env python3
"""测试 LM Studio 本地 API 连接"""

import sys
import json
import os
import requests
from typing import Optional

# LM Studio 配置
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "")  # 从环境变量读取
TIMEOUT = 30

# 请求头配置
def get_headers():
    """获取请求头（包含 API key）"""
    headers = {"Content-Type": "application/json"}
    if LM_STUDIO_API_KEY:
        headers["Authorization"] = f"Bearer {LM_STUDIO_API_KEY}"
    return headers


def print_section(title: str):
    """打印分隔线和标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_connection() -> bool:
    """测试基本连接"""
    print_section("1️⃣  测试基本连接")
    
    if LM_STUDIO_API_KEY:
        print(f"🔑 使用 API Key: {LM_STUDIO_API_KEY[:10]}...")
    else:
        print(f"⚠️  未设置 API Key（如果 LM Studio 需要认证可能会失败）")
    
    try:
        response = requests.get(
            f"{LM_STUDIO_BASE_URL}/models",
            headers=get_headers(),
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ LM Studio 连接成功！")
            print(f"   URL: {LM_STUDIO_BASE_URL}")
            return True
        elif response.status_code == 401:
            print(f"❌ 认证失败（401 Unauthorized）")
            print(f"\n💡 LM Studio 启用了 API Token 认证")
            print(f"\n🔧 获取 API Token 步骤：")
            print(f"   1. 打开 LM Studio")
            print(f"   2. 进入 Local Server 标签")
            print(f"   3. 点击 'Authentication' 或 'API Token'")
            print(f"   4. 复制显示的 token")
            print(f"\n🔧 使用 Token 运行测试：")
            print(f"   export LM_STUDIO_API_KEY='your-token-here'")
            print(f"   python scripts/test_lm_studio.py")
            return False
        else:
            print(f"❌ 连接失败，状态码: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data}")
            except:
                print(f"   响应: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 LM Studio")
        print(f"\n💡 请检查：")
        print(f"   1. LM Studio 是否在 Windows 上运行")
        print(f"   2. Local Server 是否已启动（默认端口 1234）")
        print(f"   3. WSL 是否可以访问 localhost")
        print(f"\n🔧 测试连接命令：")
        print(f"   curl {LM_STUDIO_BASE_URL}/models")
        return False
        
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False


def list_models() -> Optional[list]:
    """列出可用模型"""
    print_section("2️⃣  列出可用模型")
    
    try:
        response = requests.get(
            f"{LM_STUDIO_BASE_URL}/models",
            headers=get_headers(),
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            
            if models:
                print(f"✅ 找到 {len(models)} 个模型：")
                for i, model in enumerate(models, 1):
                    model_id = model.get("id", "unknown")
                    print(f"   {i}. {model_id}")
                return models
            else:
                print(f"⚠️  没有找到已加载的模型")
                print(f"\n💡 请在 LM Studio 中加载至少一个模型")
                return []
        else:
            print(f"❌ 获取模型列表失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 获取模型列表错误: {e}")
        return None


def test_llm_inference() -> bool:
    """测试 LLM 推理"""
    print_section("3️⃣  测试 LLM 推理")
    
    # 测试提示
    test_prompt = "请用一句话介绍你自己。"
    print(f"📝 测试提示: {test_prompt}")
    
    try:
        response = requests.post(
            f"{LM_STUDIO_BASE_URL}/chat/completions",
            headers=get_headers(),
            json={
                "model": "local-model",  # LM Studio 会自动使用已加载的模型
                "messages": [
                    {"role": "user", "content": test_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            
            print(f"✅ LLM 推理成功！")
            print(f"\n💬 回复:")
            print(f"   {content}")
            
            if usage:
                print(f"\n📊 Token 使用:")
                print(f"   - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"   - 总计: {usage.get('total_tokens', 'N/A')}")
            
            return True
        else:
            print(f"❌ 推理失败，状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（>{TIMEOUT}秒）")
        print(f"\n💡 可能原因:")
        print(f"   - 模型正在加载中")
        print(f"   - 模型过大，推理速度慢")
        print(f"   - 硬件资源不足")
        return False
        
    except Exception as e:
        print(f"❌ 推理错误: {e}")
        return False


def test_embedding() -> bool:
    """测试 Embedding 生成"""
    print_section("4️⃣  测试 Embedding 生成")
    
    test_text = "这是一个测试文本"
    embedding_model = "text-embedding-qwen3-embedding-4b"
    
    print(f"📝 测试文本: {test_text}")
    print(f"🎯 Embedding 模型: {embedding_model}")
    
    try:
        response = requests.post(
            f"{LM_STUDIO_BASE_URL}/embeddings",
            headers=get_headers(),
            json={
                "model": embedding_model,
                "input": test_text
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result["data"][0]["embedding"]
            usage = result.get("usage", {})
            
            print(f"✅ Embedding 生成成功！")
            print(f"\n📊 向量信息:")
            print(f"   - 维度: {len(embedding)}")
            print(f"   - 前5个值: {embedding[:5]}")
            
            if usage:
                print(f"   - Token 使用: {usage.get('total_tokens', 'N/A')}")
            
            return True
        else:
            print(f"❌ Embedding 生成失败，状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
            if response.status_code == 404:
                print(f"\n💡 可能原因:")
                print(f"   - Embedding 模型未加载")
                print(f"   - 模型名称不匹配")
                print(f"\n🔧 解决方案:")
                print(f"   1. 在 LM Studio 中加载 embedding 模型")
                print(f"   2. 检查模型名称是否正确")
            
            return False
            
    except Exception as e:
        print(f"❌ Embedding 生成错误: {e}")
        return False


def test_streaming() -> bool:
    """测试流式输出（可选）"""
    print_section("5️⃣  测试流式输出")
    
    print(f"📝 测试流式响应...")
    
    try:
        response = requests.post(
            f"{LM_STUDIO_BASE_URL}/chat/completions",
            headers=get_headers(),
            json={
                "model": "local-model",
                "messages": [
                    {"role": "user", "content": "数到5"}
                ],
                "stream": True,
                "max_tokens": 50
            },
            stream=True,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print(f"✅ 流式输出测试:")
            print(f"   ", end="", flush=True)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0]["delta"]
                            if "content" in delta:
                                print(delta["content"], end="", flush=True)
                        except:
                            pass
            
            print()  # 换行
            return True
        else:
            print(f"⚠️  流式输出不可用")
            return False
            
    except Exception as e:
        print(f"⚠️  流式输出测试跳过: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "🔧" * 35)
    print("     LM Studio 本地 API 连接测试")
    print("🔧" * 35)
    
    results = {
        "连接测试": False,
        "模型列表": False,
        "LLM推理": False,
        "Embedding": False,
        "流式输出": False
    }
    
    # 测试连接
    if test_connection():
        results["连接测试"] = True
        
        # 列出模型
        models = list_models()
        if models is not None:
            results["模型列表"] = True
            
            # 测试 LLM 推理
            if test_llm_inference():
                results["LLM推理"] = True
            
            # 测试 Embedding
            if test_embedding():
                results["Embedding"] = True
            
            # 测试流式输出（可选）
            if test_streaming():
                results["流式输出"] = True
    
    # 打印总结
    print_section("📊 测试总结")
    
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")
    
    # 统计结果
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n   通过: {passed_count}/{total_count}")
    
    # 最终建议
    if results["连接测试"] and results["模型列表"] and results["LLM推理"]:
        print(f"\n✅ LM Studio 配置完整，可以开始使用！")
        
        if not results["Embedding"]:
            print(f"\n⚠️  注意: Embedding 测试未通过")
            print(f"   如果需要使用本地 embedding，请在 LM Studio 中加载:")
            print(f"   text-embedding-qwen3-embedding-4b")
        
        print(f"\n🚀 下一步:")
        print(f"   1. 更新 .env 文件添加本地配置")
        print(f"   2. 更新 reme_ai/config/default.yaml 添加 local 配置")
        print(f"   3. 运行实验: python cookbook/simple_demo/import_usage_demo.py")
    else:
        print(f"\n❌ 请先解决上述问题后再继续")
        return 1
    
    print("\n" + "=" * 70 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
