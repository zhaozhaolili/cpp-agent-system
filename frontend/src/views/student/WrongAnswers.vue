<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <h2>📝 错题本</h2>
        <p style="color:#999;margin-bottom:16px;">考试中答错的题目会自动收集到这里，用于复习巩固</p>

        <el-table :data="wrongList" stripe v-loading="loading" empty-text="暂无错题，继续保持！">
          <el-table-column prop="chapter_title" label="章节" width="160" />
          <el-table-column label="题型" width="90">
            <template #default="{ row }">
              <el-tag :type="getTypeColor(row.question_type)" size="small">
                {{ getTypeLabel(row.question_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="question_text" label="题目" min-width="250" show-overflow-tooltip />
          <el-table-column label="你的答案" width="180">
            <template #default="{ row }">
              <span style="color:#F56C6C;">{{ row.student_answer || '(未作答)' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="正确答案" width="180">
            <template #default="{ row }">
              <span style="color:#67C23A;">{{ row.correct_answer }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="160">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-popconfirm title="已掌握？从错题本移除" @confirm="removeWrong(row.id)">
                <template #reference>
                  <el-button size="small" type="success" text>会了</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadWrongAnswers"
          @size-change="loadWrongAnswers"
          style="margin-top:16px;justify-content:flex-end;"
        />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import { getWrongAnswers, deleteWrongAnswer } from '../../api/student'
import { formatDate } from '../../utils/format'
import { ElMessage } from 'element-plus'

const wrongList = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

onMounted(() => loadWrongAnswers())

async function loadWrongAnswers() {
  loading.value = true
  try {
    const res = await getWrongAnswers({ page: page.value, page_size: pageSize.value })
    if (Array.isArray(res.data)) {
      wrongList.value = res.data
      total.value = res.data.length
    } else {
      wrongList.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

async function removeWrong(id) {
  try {
    await deleteWrongAnswer(id)
    ElMessage.success('已移除')
    await loadWrongAnswers()
  } catch { ElMessage.error('操作失败') }
}

function getTypeLabel(type) {
  const map = { choice: '选择题', judge: '判断题', short_answer: '简答题', programming: '编程题' }
  return map[type] || type
}

function getTypeColor(type) {
  const map = { choice: '', judge: 'warning', short_answer: 'success', programming: 'danger' }
  return map[type] || ''
}
</script>
