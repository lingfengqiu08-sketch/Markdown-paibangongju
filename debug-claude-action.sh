#!/bin/bash

echo "========================================="
echo "调试 Claude GitHub Action"
echo "========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "\n${YELLOW}1. 检查 Secrets 配置...${NC}"
gh secret list | grep -q ANTHROPIC_API_KEY
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ ANTHROPIC_API_KEY 已配置${NC}"
else
    echo -e "${RED}✗ ANTHROPIC_API_KEY 未找到${NC}"
    echo "请运行: gh secret set ANTHROPIC_API_KEY"
fi

echo -e "\n${YELLOW}2. 查看最近的 Actions 运行...${NC}"
echo "最近 3 次运行："
gh run list --limit 3

echo -e "\n${YELLOW}3. 查看最新失败的运行日志...${NC}"
LATEST_RUN=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')
if [ ! -z "$LATEST_RUN" ]; then
    echo "运行 ID: $LATEST_RUN"
    echo "查看日志: gh run view $LATEST_RUN --log"
    echo ""
    echo "错误摘要："
    gh run view $LATEST_RUN --log 2>/dev/null | grep -i "error" | head -5
fi

echo -e "\n${YELLOW}建议的修复步骤：${NC}"
echo "1. 重新设置 API 密钥："
echo "   gh secret set ANTHROPIC_API_KEY"
echo ""
echo "2. 查看完整日志："
echo "   gh run view $LATEST_RUN --web"
echo ""
echo "3. 访问 Actions 页面："
echo "   https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/actions"