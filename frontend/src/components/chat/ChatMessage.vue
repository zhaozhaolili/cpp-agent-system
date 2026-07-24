<template>
  <div :class="['chat-message', role]">
    <div class="avatar">
      <el-avatar :size="36" :icon="role === 'user' ? 'UserFilled' : 'ChatDotSquare'" />
    </div>
    <div class="content">
      <div class="markdown-body" v-html="rendered"></div>
      <div v-if="sources && sources.length" class="sources">
        <span style="font-size:12px;color:#999;">参考来源: {{ sources.join(', ') }}</span>
      </div>
      <!-- 追问按钮 -->
      <div v-if="followups && followups.length" class="followups">
        <div style="font-size:12px;color:#999;margin-bottom:6px;">继续探索：</div>
        <el-button
          v-for="(q, i) in followups"
          :key="i"
          size="small"
          text
          type="primary"
          style="margin-right:4px;margin-bottom:4px;"
          @click="$emit('followup', q)"
        >{{ q }}</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  role: { type: String, default: 'user' },
  content: { type: String, default: '' },
  sources: { type: Array, default: () => [] },
  followups: { type: Array, default: () => [] },
})

defineEmits(['followup'])

const rendered = computed(() => {
  let text = props.content || ''
  text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  text = text.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>')
  text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/\n/g, '<br/>')
  return text
})
</script>

<style scoped>
.chat-message { display: flex; gap: 12px; margin-bottom: 20px; padding: 0 16px; }
.chat-message.user { flex-direction: row-reverse; }
.chat-message.user .content { background: #409EFF; color: #fff; border-radius: 12px 12px 4px 12px; }
.chat-message.assistant .content { background: #f4f4f5; border-radius: 12px 12px 12px 4px; }
.content { max-width: 75%; padding: 12px 16px; line-height: 1.6; font-size: 14px; word-break: break-word; }
.content :deep(pre) { background: #282c34; color: #abb2bf; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 8px 0; }
.content :deep(code) { font-family: 'Consolas', monospace; font-size: 13px; }
.content :deep(strong) { font-weight: 600; }
.sources { margin-top: 8px; }
.followups { margin-top: 10px; padding-top: 8px; border-top: 1px solid #e8e8e8; }
</style>
