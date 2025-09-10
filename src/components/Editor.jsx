import React from 'react'

function Editor({ value, onChange }) {
  return (
    <div className="h-full flex flex-col">
      <div className="bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 border-b">
        编辑器
      </div>
      <textarea
        className="flex-1 p-4 font-mono text-sm resize-none focus:outline-none"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="在此输入 Markdown 内容..."
      />
    </div>
  )
}

export default Editor