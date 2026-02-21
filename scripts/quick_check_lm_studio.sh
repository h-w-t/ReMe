#!/bin/bash
# 快速检查 LM Studio 连接状态

set -e

LM_STUDIO_URL="http://localhost:1234/v1"

echo "========================================"
echo "🔍 快速检查 LM Studio 连接"
echo "========================================"
echo ""

# 检查连接
echo "1. 测试连接..."
if curl -s --max-time 5 "${LM_STUDIO_URL}/models" > /dev/null 2>&1; then
    echo "   ✅ LM Studio 连接成功"
else
    echo "   ❌ 无法连接到 LM Studio"
    echo ""
    echo "   请检查："
    echo "   - LM Studio 是否在 Windows 上运行"
    echo "   - Local Server 是否已启动（端口 1234）"
    echo ""
    echo "   测试命令: curl ${LM_STUDIO_URL}/models"
    exit 1
fi

# 列出模型
echo ""
echo "2. 检查已加载的模型..."
MODELS=$(curl -s "${LM_STUDIO_URL}/models" 2>/dev/null || echo "")

if [ -n "$MODELS" ]; then
    # 尝试解析 JSON（如果安装了 jq）
    if command -v jq &> /dev/null; then
        MODEL_COUNT=$(echo "$MODELS" | jq '.data | length')
        echo "   ✅ 找到 $MODEL_COUNT 个模型"
        echo "$MODELS" | jq -r '.data[].id' | while read -r model; do
            echo "      - $model"
        done
    else
        # 如果没有 jq，使用 grep
        if echo "$MODELS" | grep -q '"id"'; then
            echo "   ✅ 已加载模型"
            echo "$MODELS" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | while read -r model; do
                echo "      - $model"
            done
        else
            echo "   ⚠️  未找到已加载的模型"
        fi
    fi
else
    echo "   ❌ 无法获取模型列表"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ LM Studio 运行正常！"
echo "========================================"
echo ""
echo "🚀 运行完整测试:"
echo "   python scripts/test_lm_studio.py"
echo ""
