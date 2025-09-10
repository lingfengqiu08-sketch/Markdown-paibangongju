# Markdown 排版工具 - 技术方案

## 1. 项目概述

本项目是一个基于 Web 的 Markdown 排版工具，主要服务于内容创作者，特别是需要在微信公众号、知乎、掘金等平台发布文章的用户。通过提供实时预览和优化的排版样式，帮助用户快速生成适合各平台的富文本内容。

## 2. 技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────┐
│             前端应用 (SPA)                    │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  编辑器   │  │   解析器  │  │   预览器  │ │
│  │(textarea)│→ │(marked.js)│→ │  (React) │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │            样式系统                    │  │
│  │   (Tailwind CSS + Custom Themes)     │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │            本地存储                    │  │
│  │         (localStorage API)            │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### 2.2 技术栈选型

| 技术领域 | 选型 | 选择理由 |
|---------|------|---------|
| **前端框架** | React 19 | - 组件化开发<br>- 虚拟DOM高效更新<br>- 生态成熟 |
| **构建工具** | Vite 7 | - 极快的冷启动<br>- 即时热更新<br>- 零配置 |
| **Markdown解析** | Marked.js 16 | - 轻量级（~40KB）<br>- GFM支持<br>- 可扩展性强 |
| **代码高亮** | Prism.js | - 轻量级<br>- 支持150+语言<br>- 主题丰富 |
| **样式框架** | Tailwind CSS 4 | - 原子化CSS<br>- 快速开发<br>- 响应式设计 |
| **状态管理** | React Hooks | - 简单直观<br>- 无需额外依赖 |

### 2.3 数据流设计

```javascript
// 单向数据流
用户输入(Editor) 
    ↓
setState(markdown)
    ↓
解析Markdown(marked.js)
    ↓
生成HTML + 应用样式
    ↓
渲染预览(Preview)
    ↓
[可选] 导出/复制
```

**关键数据流程：**
1. 用户在编辑器输入 Markdown 文本
2. 通过 React State 管理文本状态
3. Marked.js 实时解析 Markdown 为 HTML
4. 应用主题样式并在预览区渲染
5. 自动保存到 localStorage（防抖处理）

## 3. 核心模块设计

### 3.1 组件架构

```
src/
├── App.jsx                 # 主应用，状态管理中心
├── components/
│   ├── Editor.jsx         # 编辑器组件
│   │   ├── Props: value, onChange
│   │   └── Features: 语法高亮、快捷键
│   ├── Preview.jsx        # 预览组件
│   │   ├── Props: markdown, theme
│   │   └── Features: 实时渲染、代码高亮
│   └── Toolbar.jsx        # 工具栏组件
│       ├── Props: theme, setTheme, markdown
│       └── Features: 主题切换、导出功能
├── utils/
│   ├── markdown-parser.js # Markdown解析配置
│   ├── storage.js        # 本地存储管理
│   └── export.js         # 导出功能实现
└── styles/
    ├── themes/           # 主题样式
    │   ├── wechat.css   # 微信公众号
    │   ├── zhihu.css    # 知乎
    │   └── juejin.css   # 掘金
    └── index.css        # 全局样式
```

### 3.2 核心功能模块

#### 3.2.1 Markdown 解析器配置

```javascript
// markdown-parser.js
import { marked } from 'marked'

// 配置选项
marked.setOptions({
  breaks: true,           // 支持换行
  gfm: true,              // GitHub Flavored Markdown
  headerIds: false,       // 不生成标题ID
  langPrefix: 'language-', // 代码块语言前缀
  sanitize: false,        // 不过滤HTML（信任用户输入）
  smartLists: true,       // 智能列表
  tables: true            // 支持表格
})

// 自定义渲染器
const renderer = new marked.Renderer()

// 自定义标题渲染（添加样式类）
renderer.heading = (text, level) => {
  return `<h${level} class="heading-${level}">${text}</h${level}>`
}

// 自定义代码块渲染（支持语言识别）
renderer.code = (code, language) => {
  const lang = language || 'plaintext'
  return `<pre><code class="language-${lang}">${code}</code></pre>`
}

// 自定义链接（新窗口打开）
renderer.link = (href, title, text) => {
  return `<a href="${href}" target="_blank" rel="noopener">${text}</a>`
}
```

#### 3.2.2 本地存储管理

```javascript
// storage.js
const STORAGE_KEY = 'markdown_editor_content'
const THEME_KEY = 'markdown_editor_theme'

export const storage = {
  // 保存内容（带防抖）
  saveContent: debounce((content) => {
    localStorage.setItem(STORAGE_KEY, content)
  }, 1000),
  
  // 读取内容
  getContent: () => {
    return localStorage.getItem(STORAGE_KEY) || ''
  },
  
  // 保存主题
  saveTheme: (theme) => {
    localStorage.setItem(THEME_KEY, theme)
  },
  
  // 读取主题
  getTheme: () => {
    return localStorage.getItem(THEME_KEY) || 'wechat'
  }
}
```

#### 3.2.3 导出功能实现

```javascript
// export.js
export const exportUtils = {
  // 复制HTML到剪贴板
  copyHTML: (element) => {
    const range = document.createRange()
    range.selectNode(element)
    window.getSelection().removeAllRanges()
    window.getSelection().addRange(range)
    document.execCommand('copy')
    window.getSelection().removeAllRanges()
  },
  
  // 导出Markdown文件
  downloadMarkdown: (content, filename = 'document.md') => {
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  },
  
  // 导出PDF（需要额外库）
  exportPDF: async (element) => {
    // 使用 html2pdf.js 或类似库
    // 待实现
  }
}
```

## 4. 性能优化策略

### 4.1 渲染优化

- **防抖处理**：编辑器输入使用防抖（300ms）减少解析频率
- **虚拟滚动**：长文档使用虚拟滚动提升性能
- **懒加载**：代码高亮按需加载语言包

### 4.2 内存优化

- **及时清理**：组件卸载时清理定时器和事件监听
- **内容限制**：设置最大字符数限制（如100,000字符）
- **图片优化**：图片使用懒加载和压缩

### 4.3 打包优化

```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'markdown': ['marked', 'prismjs']
        }
      }
    },
    minify: 'terser',
    cssCodeSplit: true
  }
}
```

## 5. 样式系统设计

### 5.1 主题变量系统

```css
/* 主题变量定义 */
:root {
  --primary-color: #07689f;
  --text-color: #3f3f3f;
  --bg-color: #ffffff;
  --code-bg: #f8f8f8;
  --border-color: #e1e4e8;
  --font-size-base: 16px;
  --line-height: 1.8;
}

/* 微信主题覆盖 */
.theme-wechat {
  --primary-color: #07689f;
  --h1-size: 22px;
  --h2-size: 20px;
  --h3-size: 18px;
}
```

### 5.2 响应式设计

```css
/* 移动端适配 */
@media (max-width: 768px) {
  .editor-container {
    flex-direction: column;
  }
  
  .editor, .preview {
    width: 100%;
    height: 50vh;
  }
}
```

## 6. 安全性考虑

### 6.1 XSS 防护

- 使用 `dangerouslySetInnerHTML` 时确保内容可信
- 考虑使用 DOMPurify 进行内容净化
- 限制用户输入的HTML标签

### 6.2 内容安全策略

```javascript
// 设置 CSP 头
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline';">
```

## 7. 测试策略

### 7.1 单元测试

- 测试 Markdown 解析功能
- 测试导出功能
- 测试存储功能

### 7.2 集成测试

- 测试编辑器和预览联动
- 测试主题切换
- 测试文件导入导出

### 7.3 E2E 测试

- 完整的用户流程测试
- 跨浏览器兼容性测试
- 性能测试

## 8. 部署方案

### 8.1 构建配置

```bash
# 生产构建
npm run build

# 构建产物
dist/
├── index.html
├── assets/
│   ├── index.[hash].js
│   ├── index.[hash].css
│   └── vendor.[hash].js
```

### 8.2 部署选项

1. **静态托管**：GitHub Pages, Netlify, Vercel
2. **CDN加速**：CloudFlare, 阿里云CDN
3. **容器化部署**：Docker + Nginx

### 8.3 CI/CD 流程

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm ci
      - run: npm run build
      - run: npm run test
      - uses: peaceiris/actions-gh-pages@v3
```

## 9. 监控与维护

### 9.1 错误监控

- 集成 Sentry 进行错误追踪
- 添加性能监控
- 用户行为分析

### 9.2 更新策略

- 定期更新依赖
- 安全补丁及时修复
- 功能迭代计划

## 10. 扩展性设计

### 10.1 插件系统

预留插件接口，支持：
- 自定义 Markdown 语法
- 自定义渲染器
- 自定义主题
- 第三方服务集成

### 10.2 API 设计

```javascript
// 暴露核心API
window.MarkdownEditor = {
  setContent: (content) => {},
  getContent: () => {},
  setTheme: (theme) => {},
  export: (format) => {},
  on: (event, handler) => {}
}
```

## 11. 技术债务管理

- 定期代码审查
- 重构计划
- 技术文档更新
- 知识分享会议