#!/bin/bash

echo "检查 GitHub CLI 安装状态..."
echo "================================"

# 检查 gh 是否安装
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI 已安装"
    echo "版本: $(gh --version | head -n 1)"
else
    echo "❌ GitHub CLI 未安装"
    exit 1
fi

echo ""

# 检查认证状态
echo "检查 GitHub 认证状态..."
echo "================================"
if gh auth status &> /dev/null; then
    echo "✅ 已认证到 GitHub"
    gh auth status
else
    echo "❌ 未认证，请运行: gh auth login"
    exit 1
fi

echo ""
echo "✅ 一切就绪！你现在可以继续安装 Claude GitHub App 了"