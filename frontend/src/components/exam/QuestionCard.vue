<template>
  <el-card class="question-card">
    <template #header>
      <div style="display:flex;justify-content:space-between;">
        <span>第 {{ question.index + 1 }} 题 — {{ typeLabel }}</span>
        <el-tag :type="tagType" size="small">{{ typeLabel }}</el-tag>
      </div>
    </template>

    <div class="question-text">{{ question.question }}</div>

    <!-- 选择题 -->
    <el-radio-group
      v-if="question.type === 'choice'"
      v-model="localAnswer"
      class="options-group"
      @change="onChange"
    >
      <el-radio
        v-for="(opt, idx) in question.options"
        :key="idx"
        :label="String.fromCharCode(65 + idx)"
        :value="String.fromCharCode(65 + idx)"
      >
        {{ String.fromCharCode(65 + idx) }}. {{ opt }}
      </el-radio>
    </el-radio-group>

    <!-- 判断题 -->
    <el-radio-group
      v-else-if="question.type === 'judge'"
      v-model="localAnswer"
      @change="onChange"
    >
      <el-radio label="正确" value="正确">正确</el-radio>
      <el-radio label="错误" value="错误">错误</el-radio>
    </el-radio-group>

    <!-- 简答题 -->
    <el-input
      v-else-if="question.type === 'short_answer'"
      v-model="localAnswer"
      type="textarea"
      :rows="4"
      placeholder="请输入答案..."
      @change="onChange"
    />

    <!-- 编程题（带在线运行） -->
    <div v-else-if="question.type === 'programming'">
      <el-input
        v-model="localAnswer"
        type="textarea"
        :rows="10"
        placeholder="请输入 C++ 代码..."
        class="code-input"
        @change="onChange"
      />
      <div style="margin-top:8px;display:flex;align-items:center;gap:8px;">
        <el-button type="success" :loading="running" @click="runCode">
          <el-icon><CaretRight /></el-icon> 运行代码
        </el-button>
        <el-input v-model="stdinInput" placeholder="标准输入（可选）" size="small" style="width:200px;" />
      </div>
      <div v-if="runOutput !== null" class="console" :class="{ error: runError }">
        <div class="console-header">
          <span>{{ runError ? '运行错误' : '运行输出' }}</span>
          <el-button text size="small" style="color:inherit;" @click="runOutput = null">×</el-button>
        </div>
        <pre>{{ runOutput }}</pre>
      </div>
    </div>

    <!-- 其他类型 -->
    <el-input
      v-else
      v-model="localAnswer"
      type="textarea"
      :rows="4"
      placeholder="请输入答案..."
      @change="onChange"
    />
  </el-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { runCppCode } from '../../api/exam'

const props = defineProps({
  question: { type: Object, required: true },
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'change'])
const localAnswer = ref(props.modelValue)
const running = ref(false)
const runOutput = ref(null)
const runError = ref(false)
const stdinInput = ref('')

watch(() => props.modelValue, (v) => { localAnswer.value = v })
watch(() => props.question, () => { localAnswer.value = ''; runOutput.value = null })

function onChange() {
  emit('update:modelValue', localAnswer.value)
  emit('change', { index: props.question.index, answer: localAnswer.value })
}

async function runCode() {
  if (!localAnswer.value.trim()) return
  running.value = true
  runOutput.value = null
  try {
    const res = await runCppCode(localAnswer.value, stdinInput.value)
    runError.value = !res.data.success
    runOutput.value = res.data.success ? res.data.output : res.data.error
  } catch (e) {
    runError.value = true
    runOutput.value = '运行失败：无法连接到服务器'
  } finally {
    running.value = false
  }
}

const typeLabel = computed(() => {
  const map = { choice: '选择题', judge: '判断题', short_answer: '简答题', programming: '编程题' }
  return map[props.question.type] || props.question.type
})

const tagType = computed(() => {
  const map = { choice: '', judge: 'warning', short_answer: 'success', programming: 'danger' }
  return map[props.question.type] || 'info'
})
</script>

<style scoped>
.question-card {
  margin-bottom: 16px;
}
.question-text {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 16px;
}
.options-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.code-input :deep(textarea) {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
}
.console {
  margin-top: 8px;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 6px;
  overflow: hidden;
}
.console.error {
  border: 1px solid #F56C6C;
}
.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 12px;
  background: #333;
  font-size: 12px;
}
.console pre {
  margin: 0;
  padding: 12px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}
</style>
