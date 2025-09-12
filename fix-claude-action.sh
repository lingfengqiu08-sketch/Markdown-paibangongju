#!/bin/bash

echo "========================================="
echo "修复 Claude GitHub Action - 完整方案"
echo "========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /Users/qiulingfeng/conductor/markdown-paibangongju/.conductor/paiban

echo -e "\n${YELLOW}📋 手动修复步骤：${NC}"
echo ""

echo -e "${BLUE}步骤 1: 检查和设置 API 密钥${NC}"
echo "----------------------------------------"
echo "1. 打开浏览器访问："
echo "   ${GREEN}https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/settings/secrets/actions${NC}"
echo ""
echo "2. 检查是否有 'ANTHROPIC_API_KEY'"
echo "   - 如果没有，点击 'New repository secret'"
echo "   - Name: ANTHROPIC_API_KEY"
echo "   - Value: 你的 API 密钥 (sk-ant-...)"
echo ""

echo -e "${BLUE}步骤 2: 查看 Actions 运行状态${NC}"
echo "----------------------------------------"
echo "访问 Actions 页面："
echo "   ${GREEN}https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/actions${NC}"
echo ""
echo "查看是否有运行记录，点击失败的运行查看详细日志"
echo ""

echo -e "${BLUE}步骤 3: 测试 API 密钥是否有效${NC}"
echo "----------------------------------------"
echo "创建测试文件..."

cat > test-api.py << 'EOF'
import os
import sys

# 测试 API 密钥
api_key = input("请输入你的 Anthropic API 密钥 (sk-ant-...): ").strip()

if not api_key or not api_key.startswith("sk-ant-"):
    print("❌ 无效的 API 密钥格式")
    sys.exit(1)

try:
    from anthropic import Anthropic
except ImportError:
    print("安装 Anthropic SDK...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
    from anthropic import Anthropic

try:
    client = Anthropic(api_key=api_key)
    print("🔄 测试 API 连接...")
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say 'API is working' if you can read this"}]
    )
    
    print(f"✅ API 密钥有效！")
    print(f"Claude 回复: {response.content[0].text}")
    print("\n现在你可以将这个密钥添加到 GitHub Secrets 中")
    
except Exception as e:
    print(f"❌ API 测试失败: {e}")
    print("\n可能的原因：")
    print("1. API 密钥无效或过期")
    print("2. 账户没有额度")
    print("3. 网络连接问题")
EOF

echo -e "${GREEN}✅ 测试文件已创建${NC}"
echo ""

echo -e "${BLUE}步骤 4: 运行 API 测试${NC}"
echo "----------------------------------------"
echo "运行命令："
echo "   python3 test-api.py"
echo ""

echo -e "${BLUE}步骤 5: 创建简化的 workflow${NC}"
echo "----------------------------------------"
echo "已创建简化版 workflow 文件"

cat > .github/workflows/claude-simple.yml << 'EOF'
name: Claude Test

on:
  workflow_dispatch:
  issue_comment:
    types: [created]

jobs:
  test-claude:
    runs-on: ubuntu-latest
    if: |
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'issue_comment' && 
       contains(github.event.comment.body, '@claude-test'))
    
    steps:
      - name: Test API Key
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          if [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "❌ ANTHROPIC_API_KEY is not set in secrets"
            exit 1
          fi
          echo "✅ ANTHROPIC_API_KEY is configured"
          echo "Key starts with: ${ANTHROPIC_API_KEY:0:10}..."
EOF

echo ""
echo -e "${YELLOW}📝 下一步操作：${NC}"
echo "----------------------------------------"
echo "1. 先运行 API 测试确认密钥有效："
echo "   ${GREEN}python3 test-api.py${NC}"
echo ""
echo "2. 在 GitHub 网页上添加/更新 Secret"
echo ""
echo "3. 提交新的 workflow："
echo "   ${GREEN}git add .github/workflows/claude-simple.yml${NC}"
echo "   ${GREEN}git commit -m 'Add simple Claude test workflow'${NC}"
echo "   ${GREEN}git push origin paiban${NC}"
echo ""
echo "4. 手动触发测试："
echo "   访问 Actions 页面 → Claude Test → Run workflow"
echo ""
echo "5. 在 PR 中测试："
echo "   评论 '@claude-test' 触发测试"
echo ""

echo -e "${YELLOW}🔗 有用的链接：${NC}"
echo "----------------------------------------"
echo "GitHub Secrets: https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/settings/secrets/actions"
echo "Actions 页面: https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/actions"
echo "Pull Request: https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/pull/1"
echo "Anthropic Console: https://console.anthropic.com/settings/keys"