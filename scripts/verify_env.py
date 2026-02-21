#!/usr/bin/env python3
"""验证环境变量配置是否完整并测试连接"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("=" * 70)
print("🔍 环境变量配置验证")
print("=" * 70)

# 检查必需的环境变量
required_vars = {
    "LM Studio 连接": [
        ("LM_STUDIO_API_KEY", "LM Studio API Token"),
        ("OPENAI_API_KEY", "OpenAI 标准环境变量（cookbook 使用）"),
        ("OPENAI_BASE_URL", "OpenAI Base URL（cookbook 使用）"),
    ],
    "ReMe 本地配置": [
        ("FLOW_LOCAL_LLM_API_KEY", "FlowLLM 本地 LLM API Key"),
        ("FLOW_LOCAL_LLM_BASE_URL", "FlowLLM 本地 LLM Base URL"),
        ("FLOW_LOCAL_EMBEDDING_API_KEY", "FlowLLM 本地 Embedding API Key"),
        ("FLOW_LOCAL_EMBEDDING_BASE_URL", "FlowLLM 本地 Embedding Base URL"),
    ],
}

all_ok = True

for category, vars_list in required_vars.items():
    print(f"\n{category}:")
    print("-" * 70)
    
    for var_name, description in vars_list:
        value = os.getenv(var_name)
        if value and value != "sk-xxxx":
            # 隐藏敏感信息
            if "API_KEY" in var_name or "api" in var_name.lower():
                display_value = value[:15] + "..." if len(value) > 15 else value
            else:
                display_value = value
            print(f"  ✅ {var_name}")
            print(f"     {description}")
            print(f"     值: {display_value}")
        else:
            print(f"  ❌ {var_name}")
            print(f"     {description}")
            print(f"     状态: 未设置或使用默认值")
            all_ok = False

# 测试 LM Studio 连接
print("\n" + "=" * 70)
print("🔗 测试 LM Studio 连接")
print("=" * 70)

try:
    import requests
    
    base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    response = requests.get(f"{base_url}/models", headers=headers, timeout=5)
    
    if response.status_code == 200:
        print(f"✅ LM Studio 连接成功")
        print(f"   URL: {base_url}")
        
        try:
            models = response.json().get("data", [])
            print(f"   已加载模型数量: {len(models)}")
            if models:
                print(f"\n   可用模型:")
                for model in models[:5]:  # 只显示前5个
                    print(f"     - {model.get('id', 'unknown')}")
                if len(models) > 5:
                    print(f"     ... 还有 {len(models) - 5} 个模型")
        except:
            pass
    else:
        print(f"❌ LM Studio 连接失败")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 401:
            print(f"   提示: API Key 可能有误")
        all_ok = False
        
except Exception as e:
    print(f"❌ 无法连接到 LM Studio: {e}")
    print(f"\n💡 请确保:")
    print(f"   1. LM Studio 在 Windows 上已启动")
    print(f"   2. Local Server 已启动（端口 1234）")
    print(f"   3. 至少加载了一个模型")
    all_ok = False

# 测试 OpenAI 客户端
print("\n" + "=" * 70)
print("🧪 测试 OpenAI 客户端配置")
print("=" * 70)

try:
    from openai import OpenAI
    
    # 创建客户端（会自动读取环境变量）
    client = OpenAI()
    
    print(f"✅ OpenAI 客户端创建成功")
    print(f"   Base URL: {client.base_url}")
    
    # 测试简单调用
    try:
        models = client.models.list()
        print(f"✅ 模型列表获取成功")
        print(f"   API 配置正确，可以在 cookbook 中使用")
    except Exception as e:
        print(f"⚠️  模型列表获取失败: {e}")
        all_ok = False
        
except Exception as e:
    print(f"❌ OpenAI 客户端配置失败: {e}")
    all_ok = False

# 总结
print("\n" + "=" * 70)
print("📊 配置总结")
print("=" * 70)

if all_ok:
    print("""
✅ 所有配置检查通过！

🚀 现在可以运行实验：

1. 使用本地模型（当前配置）:
   cd cookbook/frozenlake
   python run_frozenlake.py

2. 使用 ReMe with 本地模型:
   cd cookbook/simple_demo
   python import_usage_demo.py

3. 切换到在线 API:
   编辑 .env 文件，修改 OPENAI_API_KEY 和 OPENAI_BASE_URL

💡 提示:
   - 所有 cookbook 实验会自动使用 OPENAI_* 环境变量
   - 无需修改代码即可切换本地/在线模型
   - 本地模型节省 API 成本，适合大量实验
""")
else:
    print("""
⚠️  部分配置需要检查

🔧 请按以下步骤排查：

1. 确认 LM Studio 已启动并加载模型
2. 检查 .env 文件中的配置
3. 运行: python scripts/test_lm_studio.py
4. 查看文档: cat LM_STUDIO_TEST_SUMMARY.md
""")

print("=" * 70)
