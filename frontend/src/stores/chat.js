import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getChatHistory, getConversations } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const conversations = ref([])
  const isGenerating = ref(false)
  const abortController = ref(null)

  // 加载对话列表
  async function loadConversations() {
    try {
      conversations.value = await getConversations(1, 30)
    } catch (e) {
      console.error('加载对话列表失败:', e)
    }
  }

  // 加载最新对话历史
  async function loadHistory() {
    try {
      const history = await getChatHistory(1, 20)
      const msgs = history.reverse().flatMap((h) => [
        { role: 'user', content: h.question, id: h.id },
        { role: 'assistant', content: h.answer, id: h.id + '_a', sources: h.sources },
      ])
      messages.value = msgs
    } catch (e) {
      console.error('加载历史失败:', e)
    }
  }

  // 创建新对话
  function newChat() {
    messages.value = []
  }

  function addMessage(role, content, sources = []) {
    messages.value.push({ role, content, sources, id: Date.now() })
  }

  function updateLastAssistant(token) {
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'assistant') {
      last.content += token
    }
  }

  async function sendMessage(question) {
    addMessage('user', question)
    addMessage('assistant', '')
    isGenerating.value = true

    const token = localStorage.getItem('token')
    const controller = new AbortController()
    abortController.value = controller

    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question }),
        signal: controller.signal,
      })

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
                const last = messages.value[messages.value.length - 1]
                if (last) {
                  last.sources = parsed.sources || []
                  last.followups = parsed.followups || []
                }
              }
            } catch {
              updateLastAssistant(data)
            }
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        updateLastAssistant('\n\n[错误: ' + (err.message || '网络异常') + ']')
      }
    } finally {
      isGenerating.value = false
      abortController.value = null
    }
  }

  function stopGeneration() {
    abortController.value?.abort()
    isGenerating.value = false
  }

  return { messages, conversations, isGenerating, loadConversations, loadHistory, newChat, addMessage, sendMessage, stopGeneration }
})
