/**
 * SSE 流式读取 composable
 */
import { ref } from 'vue'

export function useSSE() {
  const isStreaming = ref(false)
  const controller = ref(null)

  const start = ({ question, onToken, onDone, onError }) => {
    isStreaming.value = true
    const token = localStorage.getItem('token')
    controller.value = new AbortController()

    fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ question }),
      signal: controller.value.signal,
    })
      .then(async (response) => {
        if (!response.ok) throw new Error('请求失败')
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
      .finally(() => {
        isStreaming.value = false
      })
  }

  const stop = () => {
    controller.value?.abort()
    isStreaming.value = false
  }

  return { isStreaming, start, stop }
}
