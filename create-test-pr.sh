#!/bin/bash

echo "========================================="
echo "创建测试 Pull Request"
echo "========================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /Users/qiulingfeng/conductor/markdown-paibangongju/.conductor/paiban

echo -e "\n${YELLOW}正在创建 Pull Request...${NC}"

gh pr create \
  --title "测试 Claude Code Review 功能 🤖" \
  --body "## 测试 Claude Code Review

这个 PR 包含了之前创建的功能：
- 🌀 递归迷宫游戏
- ⏰ 番茄工作法计时器

### 如何测试 Claude
在评论中输入 \`@claude\` 来触发 Claude 代码审查。

### 文件列表
- \`recursive-maze.html\` - 递归迷宫游戏界面  
- \`recursive-maze.js\` - 游戏逻辑
- \`pomodoro-timer.html\` - 番茄钟界面
- \`pomodoro-timer.js\` - 计时器逻辑

### Claude GitHub Action 配置
- ✅ Workflow 文件: \`.github/workflows/claude-code.yml\`
- ✅ API Key 已配置在 Secrets 中

---
🤖 使用 Claude Code 创建" \
  --base main \
  --head paiban

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Pull Request 创建成功！${NC}"
    echo -e "\n下一步："
    echo "1. 访问 PR 页面（上面的链接）"
    echo "2. 在评论中输入 @claude 来触发代码审查"
    echo "3. Claude 会自动审查你的代码并提供反馈"
else
    echo -e "\n${YELLOW}如果失败，你也可以手动创建 PR：${NC}"
    echo "访问: https://github.com/lingfengqiu08-sketch/Markdown-paibangongju/compare/main...paiban"
    echo "点击 'Create pull request' 按钮"
fi