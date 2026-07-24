/**
 * 聊天 API — SSE 流式对话
 */
import { useUserStore } from '../stores/user'

const BASE = '/api/v1/chat'

/**
 * 流式对话（通过 fetch ReadableStream）
 * @param {string} question
 * @param {function} onToken 每收到一个 token 调用
 * @param {function} onDone 完成时调用
 * @param {function} onError 错误时调用
 * @returns {AbortController} 用于取消请求
 */
export function streamChat(question, { onToken, onDone, onError }) {
  const token = localStorage.getItem('token')
  const controller = new AbortController()

  fetch(`${BASE}/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ question }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        const err = await response.json()
        onError?.(err.detail || '请求失败')
        return
      }
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            try {
              const parsed = JSON.parse(data)
              if (parsed.done) {
                onDone?.(parsed)
              } else {
                onToken?.(data)
              }
            } catch {
              // 纯文本 token
              onToken?.(data)
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError?.(err.message || '网络错误')
      }
    })

  return controller
}

/**
 * 获取单条对话完整内容
 */
export async function getChatDetail(id) {
  const token = localStorage.getItem('token')
  const res = await fetch(`${BASE}/history/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('获取对话失败')
  return res.json()
}

/**
 * 获取对话列表
 */
export async function getConversations(page = 1, pageSize = 30) {
  const token = localStorage.getItem('token')
  const res = await fetch(`${BASE}/conversations?page=${page}&page_size=${pageSize}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('获取列表失败')
  const data = await res.json()
  return Array.isArray(data) ? data : (data.items || [])
}

/**
 * 删除单条对话
 */
export async function deleteChat(id) {
  const token = localStorage.getItem('token')
  const res = await fetch(`${BASE}/history/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('删除失败')
  return res.json()
}

/**
 * 清空所有对话
 */
export async function deleteAllChats() {
  const token = localStorage.getItem('token')
  const res = await fetch(`${BASE}/history`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('清空失败')
  return res.json()
}

/**
 * 获取对话历史
 */
export async function getChatHistory(page = 1, pageSize = 20) {
  const token = localStorage.getItem('token')
  const res = await fetch(`${BASE}/history?page=${page}&page_size=${pageSize}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('获取历史失败')
  const data = await res.json()
  return Array.isArray(data) ? data : (data.items || [])
}
