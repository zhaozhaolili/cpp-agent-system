<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <h2 class="page-title">C++ 在线编程</h2>
        <p class="page-subtitle">编写代码，点击运行查看输出（支持 C++17）</p>

        <div style="display:flex;gap:20px;">
          <!-- 代码编辑区 -->
          <div style="flex:1;">
            <div style="background:#1e293b;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);">
              <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 16px;background:#0f172a;">
                <div style="display:flex;gap:6px;">
                  <span style="width:10px;height:10px;border-radius:50%;background:#ef4444;"></span>
                  <span style="width:10px;height:10px;border-radius:50%;background:#f59e0b;"></span>
                  <span style="width:10px;height:10px;border-radius:50%;background:#10b981;"></span>
                </div>
                <span style="font-size:12px;color:#94a3b8;">main.cpp</span>
                <el-button size="small" type="primary" :loading="running" @click="runCode" :icon="VideoPlay">
                  运行 (Ctrl+Enter)
                </el-button>
              </div>
              <textarea
                ref="editorRef"
                v-model="code"
                class="code-editor"
                spellcheck="false"
                @keydown="handleEditorKeydown"
              ></textarea>
            </div>
          </div>

          <!-- 输入输出区 -->
          <div style="width:340px;display:flex;flex-direction:column;gap:16px;">
            <!-- 输入 -->
            <el-card header="标准输入 (stdin)" style="flex-shrink:0;">
              <el-input
                v-model="stdin"
                type="textarea"
                :rows="4"
                placeholder="程序需要读取的输入内容（可选）"
              />
            </el-card>

            <!-- 输出 -->
            <el-card header="运行结果" style="flex:1;">
              <div v-if="running" style="text-align:center;padding:20px;">
                <el-icon class="is-loading" :size="32"><Loading /></el-icon>
                <p style="color:#94a3b8;margin-top:8px;">编译运行中...</p>
              </div>
              <pre v-else-if="output" class="output-area" :class="{ 'output-error': hasError }">{{ output }}</pre>
              <el-empty v-else description="点击「运行」查看结果" :image-size="48" />
            </el-card>
          </div>
        </div>

        <!-- 快捷示例 -->
        <el-card style="margin-top:20px;">
          <template #header><span>快捷示例</span></template>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <el-button v-for="ex in examples" :key="ex.label" size="small" @click="code = ex.code">{{ ex.label }}</el-button>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import { runCppCode } from '../../api/exam'
import { ElMessage } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'

const running = ref(false)
const output = ref('')
const hasError = ref(false)
const editorRef = ref(null)

const code = ref(`#include <iostream>
#include <vector>
#include <string>

int main() {
    std::cout << "Hello, C++ World!" << std::endl;

    // 试试更多示例 ↓

    return 0;
}`)

const stdin = ref('')

const examples = [
  { label: 'Hello World', code: `#include <iostream>\n\nint main() {\n    std::cout << "Hello, C++ World!" << std::endl;\n    return 0;\n}` },
  { label: 'FizzBuzz', code: `#include <iostream>\n\nint main() {\n    for (int i = 1; i <= 20; i++) {\n        if (i % 3 == 0 && i % 5 == 0) std::cout << "FizzBuzz ";\n        else if (i % 3 == 0) std::cout << "Fizz ";\n        else if (i % 5 == 0) std::cout << "Buzz ";\n        else std::cout << i << " ";\n    }\n    std::cout << std::endl;\n    return 0;\n}` },
  { label: 'Vector Sort', code: `#include <iostream>\n#include <vector>\n#include <algorithm>\n\nint main() {\n    std::vector<int> v = {5, 2, 8, 1, 9};\n    std::sort(v.begin(), v.end());\n    std::cout << "Sorted: ";\n    for (int x : v) std::cout << x << " ";\n    std::cout << std::endl;\n    return 0;\n}` },
  { label: 'Class & Object', code: `#include <iostream>\n#include <string>\n\nclass Student {\npublic:\n    std::string name;\n    int score;\n    Student(std::string n, int s) : name(n), score(s) {}\n    void display() {\n        std::cout << name << " score: " << score << std::endl;\n    }\n};\n\nint main() {\n    Student s("Alice", 95);\n    s.display();\n    return 0;\n}` },
  { label: 'Template', code: `#include <iostream>\n\ntemplate<typename T>\nT mymax(T a, T b) {\n    return a > b ? a : b;\n}\n\nint main() {\n    std::cout << "max(3, 7) = " << mymax(3, 7) << std::endl;\n    std::cout << "max(3.14, 2.71) = " << mymax(3.14, 2.71) << std::endl;\n    return 0;\n}` },
]

async function runCode() {
  if (!code.value.trim()) {
    ElMessage.warning('请输入代码')
    return
  }
  running.value = true
  output.value = ''
  hasError.value = false
  try {
    const res = await runCppCode(code.value, stdin.value)
    const data = res.data
    if (data.success) {
      output.value = data.output || '(无输出)'
      hasError.value = false
    } else {
      output.value = data.error || data.output || '编译/运行错误'
      hasError.value = true
    }
  } catch (e) {
    output.value = '请求失败: ' + (e.response?.data?.detail || e.message || '未知错误')
    hasError.value = true
  } finally {
    running.value = false
  }
}

function handleEditorKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    runCode()
    return
  }
  if (e.key === 'Tab') {
    e.preventDefault()
    const start = e.target.selectionStart
    const end = e.target.selectionEnd
    code.value = code.value.substring(0, start) + '    ' + code.value.substring(end)
    nextTick(() => {
      e.target.selectionStart = e.target.selectionEnd = start + 4
    })
  }
}
</script>

<style scoped>
.code-editor {
  width: 100%; height: 420px;
  background: #1e293b; color: #e2e8f0;
  border: none; outline: none; resize: vertical;
  padding: 16px 20px;
  font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
  font-size: 14px; line-height: 1.7;
  tab-size: 4;
}
.output-area {
  background: #f8fafc; border-radius: 6px; padding: 12px 16px;
  margin: 0; font-size: 13px; line-height: 1.6;
  white-space: pre-wrap; word-break: break-word;
  max-height: 280px; overflow: auto;
  color: #334155;
}
.output-error {
  background: #fef2f2; color: #dc2626;
}
</style>
