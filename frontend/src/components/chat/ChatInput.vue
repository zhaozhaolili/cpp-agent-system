<template>
  <div class="chat-input">
    <el-input
      v-model="inputText"
      type="textarea"
      :rows="3"
      :placeholder="placeholder"
      :disabled="disabled"
      @keydown.enter.exact="handleSend"
    />
    <div class="actions">
      <span class="hint">Enter 发送</span>
      <el-button v-if="disabled" type="danger" @click="$emit('stop')">停止生成</el-button>
      <el-button v-else type="primary" :disabled="!inputText.trim()" @click="handleSend">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  placeholder: { type: String, default: '输入你的 C++ 问题...' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['send', 'stop'])

const inputText = ref('')

function handleSend() {
  if (props.disabled) return
  const text = inputText.value.trim()
  if (!text) return
  emit('send', text)
  inputText.value = ''
}
</script>

<style scoped>
.chat-input {
  padding: 16px;
  border-top: 1px solid #e6e6e6;
  background: #fff;
}
.actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.hint {
  font-size: 12px;
  color: #999;
  margin-right: auto;
}
</style>
