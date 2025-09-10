import React, { useEffect, useRef } from 'react'
import { parseMarkdown } from '../utils/markdown-parser'
import Prism from 'prismjs'
import 'prismjs/themes/prism-tomorrow.css'

function Preview({ markdown, theme }) {
  const previewRef = useRef(null)

  useEffect(() => {
    if (previewRef.current) {
      const html = parseMarkdown(markdown)
      previewRef.current.innerHTML = html
      
      // Highlight code blocks
      Prism.highlightAllUnder(previewRef.current)
    }
  }, [markdown])

  return (
    <div className="h-full flex flex-col">
      <div className="bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 border-b">
        预览
      </div>
      <div className="flex-1 overflow-auto p-4">
        <div 
          ref={previewRef}
          className={`markdown-body theme-${theme}`}
        />
      </div>
    </div>
  )
}

export default Preview