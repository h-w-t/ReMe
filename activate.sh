#!/bin/bash
# ReMe 环境激活脚本
# 使用方法: source activate.sh

export PATH="$HOME/.local/bin:$PATH"
source .venv/bin/activate

echo "✓ ReMe 开发环境已激活"
echo "  - Python: $(python --version)"
echo "  - uv: $(uv --version)"
echo "  - reme_ai: $(python -c 'import reme_ai; print(reme_ai.__version__)' 2>/dev/null || echo 'N/A')"
echo "  - reme: $(python -c 'import reme; print(reme.__version__)' 2>/dev/null || echo 'N/A')"
echo ""
echo "可用命令："
echo "  - python: Python 解释器"
echo "  - uv: UV 包管理器"
echo "  - reme: ReMe HTTP 服务 (V1)"
echo "  - reme2: ReMe 命令行工具 (V2)"
echo ""
echo "快速开始："
echo "  - 运行 SimpleDemo: cd cookbook/simple_demo && python import_usage_demo.py"
echo "  - 运行 FrozenLake: cd cookbook/frozenlake && python run_frozenlake.py --help"
echo ""
echo "注意: 请确保 .env 文件中已配置 API keys"
