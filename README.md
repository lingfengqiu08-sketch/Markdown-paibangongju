# Markdown 排版工具

一个简洁高效的 Markdown 排版工具，支持实时预览和多种排版样式。

## 功能特性

- 📝 实时 Markdown 编辑与预览
- 🎨 多种排版主题（微信公众号、知乎、掘金）
- 💡 语法高亮
- 📋 一键复制 HTML
- 📱 响应式设计

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 技术栈

- React - UI 框架
- Vite - 构建工具
- Marked - Markdown 解析器
- Prism.js - 代码高亮
- Tailwind CSS - 样式框架

## 项目结构

```
src/
├── components/       # React 组件
│   ├── Editor.jsx   # 编辑器组件
│   ├── Preview.jsx  # 预览组件
│   └── Toolbar.jsx  # 工具栏组件
├── styles/          # 样式文件
│   └── themes/      # 主题样式
├── utils/           # 工具函数
│   └── markdown-parser.js  # Markdown 解析器
├── App.jsx          # 主应用组件
├── main.jsx         # 应用入口
└── index.css        # 全局样式
```

## 使用说明

1. 在左侧编辑器输入 Markdown 内容
2. 右侧实时预览排版效果
3. 选择合适的主题样式
4. 点击"复制 HTML"按钮复制格式化后的内容
5. 粘贴到目标平台（如微信公众号编辑器）

## License

MIT