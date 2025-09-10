import React, { useState } from 'react'
import Editor from './components/Editor'
import Preview from './components/Preview'
import Toolbar from './components/Toolbar'

function App() {
  const [markdown, setMarkdown] = useState('# 欢迎使用 Markdown 排版工具\n\n开始输入您的 Markdown 内容...')
  const [theme, setTheme] = useState('wechat')

  return (
    <div className="h-screen flex flex-col">
      <Toolbar theme={theme} setTheme={setTheme} markdown={markdown} />
      <div className="flex-1 flex overflow-hidden">
        <div className="w-1/2 border-r">
          <Editor value={markdown} onChange={setMarkdown} />
        </div>
        <div className="w-1/2 overflow-auto">
          <Preview markdown={markdown} theme={theme} />
        </div>
      </div>
    </div>
  )
}

export default App