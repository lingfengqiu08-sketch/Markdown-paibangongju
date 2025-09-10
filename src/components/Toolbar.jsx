import React from 'react'

function Toolbar({ theme, setTheme, markdown }) {
  const copyToClipboard = () => {
    const preview = document.querySelector('.markdown-body')
    if (preview) {
      const range = document.createRange()
      range.selectNode(preview)
      window.getSelection().removeAllRanges()
      window.getSelection().addRange(range)
      document.execCommand('copy')
      window.getSelection().removeAllRanges()
      alert('已复制到剪贴板')
    }
  }

  return (
    <div className="bg-white border-b px-4 py-2 flex items-center justify-between">
      <h1 className="text-xl font-bold">Markdown 排版工具</h1>
      
      <div className="flex items-center gap-4">
        <select 
          value={theme} 
          onChange={(e) => setTheme(e.target.value)}
          className="border rounded px-3 py-1"
        >
          <option value="wechat">微信公众号</option>
          <option value="zhihu">知乎</option>
          <option value="juejin">掘金</option>
        </select>
        
        <button
          onClick={copyToClipboard}
          className="bg-blue-500 text-white px-4 py-1 rounded hover:bg-blue-600 transition"
        >
          复制 HTML
        </button>
      </div>
    </div>
  )
}

export default Toolbar