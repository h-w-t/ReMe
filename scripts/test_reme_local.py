#!/usr/bin/env python3
"""测试 ReMe 使用 LM Studio 本地模型"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("🧪 测试 ReMe + LM Studio 本地模型集成")
print("=" * 70)

# 测试导入
try:
    from reme_ai import ReMeApp
    print("✅ ReMe 导入成功")
except Exception as e:
    print(f"❌ ReMe 导入失败: {e}")
    sys.exit(1)

print("\n" + "-" * 70)
print("1️⃣  测试使用本地 LLM 配置")
print("-" * 70)

try:
    app_local_llm = ReMeApp(
        "llm.default=local",  # 使用 local 配置
        "vector_store.default.backend=memory"
    )
    print("✅ 本地 LLM 配置成功")
    print(f"   使用模型: qwen/qwen3-8b")
    print(f"   Base URL: http://localhost:1234/v1")
except Exception as e:
    print(f"❌ 本地 LLM 配置失败: {e}")

print("\n" + "-" * 70)
print("2️⃣  测试使用本地 Embedding 配置")
print("-" * 70)

try:
    app_local_embedding = ReMeApp(
        "llm.default=local",
        "embedding_model.default=local",
        "vector_store.default=local"
    )
    print("✅ 本地 Embedding 配置成功")
    print(f"   Embedding 模型: text-embedding-qwen3-embedding-4b")
    print(f"   向量维度: 2560")
except Exception as e:
    print(f"❌ 本地 Embedding 配置失败: {e}")

print("\n" + "-" * 70)
print("3️⃣  测试混合配置（LLM本地 + Embedding在线）")
print("-" * 70)

try:
    app_hybrid = ReMeApp(
        "llm.default=local",  # LLM 使用本地
        "embedding_model.default=default",  # Embedding 使用在线
        "vector_store.default.backend=memory"
    )
    print("✅ 混合配置成功")
    print(f"   LLM: 本地 qwen/qwen3-8b")
    print(f"   Embedding: 在线 text-embedding-v4")
except Exception as e:
    print(f"❌ 混合配置失败: {e}")

print("\n" + "-" * 70)
print("4️⃣  测试使用更大的本地模型（14B）")
print("-" * 70)

try:
    app_local_14b = ReMeApp(
        "llm.default=local_14b",  # 使用 14B 模型
        "vector_store.default.backend=memory"
    )
    print("✅ 14B 模型配置成功")
    print(f"   使用模型: qwen/qwen3-14b")
except Exception as e:
    print(f"❌ 14B 模型配置失败: {e}")

print("\n" + "=" * 70)
print("📊 配置对比")
print("=" * 70)

configs = [
    ("完全在线", "llm.default=default", "适合复杂推理任务"),
    ("完全本地", "llm.default=local, embedding_model.default=local", "节省成本，适合大量调用"),
    ("混合模式", "llm.default=local, embedding_model.default=default", "平衡成本和质量"),
    ("本地14B", "llm.default=local_14b", "本地高性能推理"),
]

for name, config, desc in configs:
    print(f"\n{name}:")
    print(f"  配置: {config}")
    print(f"  说明: {desc}")

print("\n" + "=" * 70)
print("✅ ReMe 本地模型配置测试完成！")
print("=" * 70)

print("\n💡 使用示例：")
print("""
# 在你的实验代码中使用本地模型：
from reme_ai import ReMeApp

# 方式 1: 使用配置名称
app = ReMeApp(
    "llm.default=local",
    "embedding_model.default=local",
    "vector_store.default=local"
)

# 方式 2: 直接指定参数
app = ReMeApp(
    "llm.default.backend=openai_compatible",
    "llm.default.base_url=http://localhost:1234/v1",
    "llm.default.model_name=qwen/qwen3-8b",
    "embedding_model.default.base_url=http://localhost:1234/v1",
    "embedding_model.default.model_name=text-embedding-qwen3-embedding-4b"
)

# 现在可以使用 app 进行各种记忆操作
""")

print("\n🚀 下一步：")
print("  1. 运行 cookbook 中的实验")
print("  2. 根据任务复杂度选择合适的配置")
print("  3. 监控成本和性能差异")
print()
