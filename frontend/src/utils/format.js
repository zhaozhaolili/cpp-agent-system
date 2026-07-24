/**
 * 格式化工具函数
 */

export function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export function formatScore(score) {
  if (score == null) return '-'
  return `${Math.round(score)}分`
}

export function truncate(str, len = 100) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '...' : str
}

export function getFileTypeIcon(fileType) {
  const map = {
    '.pdf': 'Document',
    '.pptx': 'DataAnalysis',
    '.ppt': 'DataAnalysis',
    '.docx': 'Document',
    '.doc': 'Document',
    '.md': 'Memo',
    '.txt': 'Tickets',
  }
  return map[fileType] || 'Folder'
}

export function getExamStatusText(status) {
  const map = {
    pending: '待学习',
    in_progress: '进行中',
    completed: '已完成',
  }
  return map[status] || status
}

export function getExamStatusType(status) {
  const map = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
  }
  return map[status] || 'info'
}
