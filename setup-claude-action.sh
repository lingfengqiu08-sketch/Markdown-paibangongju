#!/bin/bash

echo "========================================="
echo "设置 Claude GitHub Action"
echo "========================================="

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 进入项目目录
cd /Users/qiulingfeng/conductor/markdown-paibangongju/.conductor/paiban

echo -e "\n${YELLOW}步骤 1: 设置默认仓库...${NC}"
gh repo set-default lingfengqiu08-sketch/Markdown-paibangongju
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 默认仓库设置成功${NC}"
else
    echo -e "${RED}✗ 设置默认仓库失败${NC}"
    exit 1
fi

echo -e "\n${YELLOW}步骤 2: 添加 Anthropic API 密钥到 GitHub Secrets...${NC}"
echo "请输入你的 Anthropic API 密钥 (sk-ant-...):"
echo "输入完成后按 Enter，然后按 Ctrl+D 确认"
echo "----------------------------------------"
gh secret set ANTHROPIC_API_KEY
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ API 密钥添加成功${NC}"
else
    echo -e "${RED}✗ API 密钥添加失败${NC}"
    echo "你可以手动访问: https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/settings/secrets/actions"
    echo "添加名为 ANTHROPIC_API_KEY 的 secret"
fi

echo -e "\n${YELLOW}步骤 3: 提交 workflow 文件...${NC}"
# 检查是否已经有 workflow 文件
if [ -f .github/workflows/claude-code.yml ]; then
    git add .github/workflows/claude-code.yml
    git commit -m "Add Claude Code GitHub Action workflow"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Workflow 文件已提交${NC}"
        
        echo -e "\n${YELLOW}步骤 4: 推送到 GitHub...${NC}"
        git push origin paiban
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 成功推送到 GitHub${NC}"
        else
            echo -e "${RED}✗ 推送失败，请手动运行: git push origin paiban${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Workflow 文件可能已经提交过了${NC}"
    fi
else
    echo -e "${RED}✗ 未找到 workflow 文件${NC}"
fi

echo -e "\n${YELLOW}步骤 5: 验证设置...${NC}"
echo "正在检查 Secrets..."
gh secret list | grep ANTHROPIC_API_KEY > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ ANTHROPIC_API_KEY 已配置${NC}"
else
    echo -e "${RED}✗ ANTHROPIC_API_KEY 未找到${NC}"
fi

echo -e "\n========================================="
echo -e "${GREEN}设置完成！${NC}"
echo -e "========================================="
echo ""
echo "下一步："
echo "1. 创建一个 Pull Request 来测试 Claude Code Review"
echo "2. 在 PR 中评论 '@claude' 来触发代码审查"
echo ""
echo "GitHub Actions 页面："
echo "https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/actions"
echo ""
echo "如需手动配置 Secrets，访问："
echo "https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/settings/secrets/actions"