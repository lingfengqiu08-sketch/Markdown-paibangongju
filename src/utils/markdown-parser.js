import { marked } from 'marked'

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: false,
  langPrefix: 'language-',
  mangle: false,
  pedantic: false,
  sanitize: false,
  smartLists: true,
  smartypants: false,
  xhtml: false
})

// Custom renderer for better formatting
const renderer = new marked.Renderer()

// Custom heading renderer
renderer.heading = function(text, level) {
  return `<h${level} class="heading-${level}">${text}</h${level}>`
}

// Custom code block renderer
renderer.code = function(code, language) {
  const lang = language || 'plaintext'
  return `<pre><code class="language-${lang}">${code}</code></pre>`
}

// Custom link renderer
renderer.link = function(href, title, text) {
  return `<a href="${href}" target="_blank" rel="noopener noreferrer" title="${title || text}">${text}</a>`
}

// Custom image renderer
renderer.image = function(href, title, text) {
  return `<img src="${href}" alt="${text}" title="${title || text}" style="max-width: 100%;" />`
}

// Custom table renderer
renderer.table = function(header, body) {
  return `<div class="table-wrapper"><table>${header}${body}</table></div>`
}

marked.use({ renderer })

export function parseMarkdown(markdown) {
  return marked(markdown)
}