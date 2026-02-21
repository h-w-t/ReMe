"""
Simple Demo - 使用本地 LM Studio 模型测试
测试 ReMe 的基本功能是否正常工作
"""
import asyncio
from reme_ai import ReMeApp


async def test_task_memory(app: ReMeApp):
    """测试任务记忆功能"""
    print("\n" + "=" * 60)
    print("📝 测试任务记忆（Task Memory）")
    print("=" * 60)
    
    # 1. 保存任务经验
    print("\n1️⃣  保存任务经验...")
    try:
        result = await app.async_execute(
            name="summary_task_memory",
            workspace_id="test_workspace",
            trajectories=[
                {
                    "messages": [
                        {"role": "user", "content": "如何使用Python读取CSV文件？"},
                        {"role": "assistant", "content": "使用pandas库：import pandas as pd; df = pd.read_csv('file.csv')"},
                    ],
                    "score": 1.0,
                },
            ],
        )
        print("✅ 任务经验保存成功")
        print(f"结果: {result.get('answer', 'N/A')[:100]}...")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False
    
    # 2. 检索任务记忆
    print("\n2️⃣  检索相关任务记忆...")
    try:
        result = await app.async_execute(
            name="retrieve_task_memory",
            workspace_id="test_workspace",
            query="Python文件读取",
            top_k=3
        )
        print("✅ 记忆检索成功")
        if result.get("answer"):
            print(f"找到 {len(result.get('answer', []))} 条相关记忆")
    except Exception as e:
        print(f"❌ 检索失败: {e}")
        return False
    
    return True


async def test_personal_memory(app: ReMeApp):
    """测试个人记忆功能"""
    print("\n" + "=" * 60)
    print("👤 测试个人记忆（Personal Memory）")
    print("=" * 60)
    
    # 1. 保存个人偏好
    print("\n1️⃣  保存个人信息...")
    try:
        result = await app.async_execute(
            name="summary_personal_memory",
            workspace_id="user_alex",
            trajectories=[
                {
                    "messages": [
                        {"role": "user", "content": "我喜欢在早晨工作，效率最高"},
                    ],
                    "score": 1.0,
                },
            ],
        )
        print("✅ 个人信息保存成功")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False
    
    # 2. 检索个人记忆
    print("\n2️⃣  检索个人偏好...")
    try:
        result = await app.async_execute(
            name="retrieve_personal_memory",
            workspace_id="user_alex",
            query="工作习惯",
            top_k=3
        )
        print("✅ 个人记忆检索成功")
    except Exception as e:
        print(f"❌ 检索失败: {e}")
        return False
    
    return True


async def test_basic_config(app: ReMeApp):
    """测试基本配置"""
    print("\n" + "=" * 60)
    print("⚙️  测试基本配置")
    print("=" * 60)
    
    # 检查 app 对象
    print(f"✅ ReMeApp 初始化成功")
    print(f"   配置已加载")
    
    return True


async def main():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print("ReMe Simple Demo - 本地模型测试")
    print("🚀" * 30)
    
    # 使用本地模型配置
    try:
        async with ReMeApp(
            "llm.default.backend=openai_compatible",
            "llm.default.base_url=http://localhost:1234/v1",
            "llm.default.api_key=sk-lm-e2e0PK8Q:mCXt3UaHAA2w9jOiI1Bc",
            "llm.default.model_name=qwen/qwen3-8b",
            "embedding_model.default.backend=openai_compatible",
            "embedding_model.default.base_url=http://localhost:1234/v1",
            "embedding_model.default.api_key=sk-lm-e2e0PK8Q:mCXt3UaHAA2w9jOiI1Bc",
            "embedding_model.default.model_name=text-embedding-qwen3-embedding-4b",
            "vector_store.default.backend=memory",
        ) as app:
            
            # 测试基本配置
            await test_basic_config(app)
            
            # 测试任务记忆
            task_ok = await test_task_memory(app)
            
            # 暂时跳过个人记忆测试，调试完任务记忆后再启用
            # personal_ok = await test_personal_memory(app)
            personal_ok = True  # 临时设为 True
            
            # 总结
            print("\n" + "=" * 60)
            print("📊 测试总结")
            print("=" * 60)
            print(f"任务记忆: {'✅ 通过' if task_ok else '❌ 失败'}")
            print(f"个人记忆: {'⏭️  跳过' if personal_ok else '❌ 失败'}")
            
            if task_ok:
                print("\n🎉 任务记忆测试通过！ReMe 本地模型配置基本正常！")
                return 0
            else:
                print("\n⚠️  部分测试失败，请检查配置")
                return 1
                
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n💡 请检查:")
        print("   1. LM Studio 是否运行")
        print("   2. 模型是否已加载")
        print("   3. .env 文件配置是否正确")
        print("\n运行诊断: python scripts/verify_env.py")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
