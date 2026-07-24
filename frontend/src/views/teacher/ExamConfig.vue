<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h2>考核配置</h2>
          <el-button type="primary" @click="showDialog = true">添加考核</el-button>
        </div>

        <el-table :data="exams" stripe v-loading="loading" empty-text="暂无考核配置">
          <el-table-column prop="chapter_title" label="章节" width="200" />
          <el-table-column label="题型分布" min-width="300">
            <template #default="{ row }">
              <el-tag v-if="row.choice_count" style="margin-right:4px;">选择 {{ row.choice_count }}</el-tag>
              <el-tag v-if="row.truefalse_count" type="warning" style="margin-right:4px;">判断 {{ row.truefalse_count }}</el-tag>
              <el-tag v-if="row.essay_count" type="success" style="margin-right:4px;">简答 {{ row.essay_count }}</el-tag>
              <el-tag v-if="row.programming_count" type="danger">编程 {{ row.programming_count }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="知识点" min-width="200">
            <template #default="{ row }">
              <el-tag v-for="kp in row.knowledge_points" :key="kp" size="small" style="margin-right:4px;">{{ kp }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" @click="viewResults(row)">查看成绩</el-button>
              <el-popconfirm title="确认删除该考核？相关的考试记录和错题也会被删除。" @confirm="handleDelete(row.id)">
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
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
          @current-change="loadExams"
          @size-change="loadExams"
          style="margin-top:16px;justify-content:flex-end;"
        />

        <!-- 添加考核弹窗 -->
        <el-dialog v-model="showDialog" title="添加章节考核" width="500px" @close="resetForm">
          <el-form :model="form" label-width="100px">
            <el-form-item label="选择章节">
              <el-select v-model="form.chapter_id" placeholder="请选择" style="width:100%;">
                <el-option v-for="ch in chapters" :key="ch.id" :label="ch.title" :value="ch.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="总题数">
              <el-input-number v-model="form.total_questions" :min="1" :max="20" />
            </el-form-item>
            <el-form-item label="选择题">
              <el-input-number v-model="form.choice_count" :min="0" :max="10" />
            </el-form-item>
            <el-form-item label="判断题">
              <el-input-number v-model="form.truefalse_count" :min="0" :max="10" />
            </el-form-item>
            <el-form-item label="简答题">
              <el-input-number v-model="form.essay_count" :min="0" :max="10" />
            </el-form-item>
            <el-form-item label="编程题">
              <el-input-number v-model="form.programming_count" :min="0" :max="5" />
            </el-form-item>
            <el-form-item label="时间限制">
              <el-input-number v-model="form.time_limit_minutes" :min="0" :max="180" :step="5" />
              <span style="margin-left:8px;font-size:12px;color:#94a3b8;">分钟（0=不限时）</span>
            </el-form-item>
            <el-form-item label="知识点">
              <el-input v-model="knowledgeInput" placeholder="逗号分隔，如: AVL树,平衡调整" />
            </el-form-item>
            <el-form-item label="评价维度">
              <el-input v-model="dimensionInput" placeholder="逗号分隔，默认: 知识掌握,基础概念,综合分析" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showDialog = false">取消</el-button>
            <el-button type="primary" :loading="submitting" @click="createExam">确定</el-button>
          </template>
        </el-dialog>

        <!-- 成绩弹窗 -->
        <el-dialog v-model="showResults" title="考核成绩" width="600px">
          <el-table :data="results" stripe>
            <el-table-column prop="student_name" label="学生" />
            <el-table-column prop="score" label="成绩">
              <template #default="{ row }">{{ row.score != null ? Math.round(row.score) : '-' }}</template>
            </el-table-column>
            <el-table-column prop="completed_at" label="完成时间">
              <template #default="{ row }">{{ formatDate(row.completed_at) }}</template>
            </el-table-column>
          </el-table>
        </el-dialog>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import { getTeacherExams, createExamConfig, getExamResults, deleteExamConfig } from '../../api/exam'
import { getChapters } from '../../api/teacher'
import { formatDate } from '../../utils/format'
import { ElMessage } from 'element-plus'

const exams = ref([])
const chapters = ref([])
const loading = ref(false)
const submitting = ref(false)
const showDialog = ref(false)
const showResults = ref(false)
const results = ref([])
const knowledgeInput = ref('')
const dimensionInput = ref('知识掌握情况,基础概念理解,综合分析能力')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const form = ref({
  chapter_id: null,
  total_questions: 6,
  choice_count: 2,
  truefalse_count: 2,
  essay_count: 2,
  programming_count: 0,
  time_limit_minutes: 0,
  knowledge_points: [],
  evaluation_dimensions: ['知识掌握情况', '基础概念理解', '综合分析能力'],
})

onMounted(async () => {
  await loadExams()
  try {
    const res = await getChapters()
    chapters.value = res.data
  } catch { /* ignore */ }
})

async function loadExams() {
  loading.value = true
  try {
    const res = await getTeacherExams({ page: page.value, page_size: pageSize.value })
    if (Array.isArray(res.data)) {
      exams.value = res.data
      total.value = res.data.length
    } else {
      exams.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } finally { loading.value = false }
}

async function createExam() {
  const kp = knowledgeInput.value.split(',').map(s => s.trim()).filter(Boolean)
  const dims = dimensionInput.value.split(',').map(s => s.trim()).filter(Boolean)
  submitting.value = true
  try {
    await createExamConfig({
      chapter_id: form.value.chapter_id,
      total_questions: form.value.total_questions,
      choice_count: form.value.choice_count,
      truefalse_count: form.value.truefalse_count,
      essay_count: form.value.essay_count,
      programming_count: form.value.programming_count,
      time_limit_minutes: form.value.time_limit_minutes,
      knowledge_points: kp,
      evaluation_dimensions: dims.length ? dims : form.value.evaluation_dimensions,
    })
    ElMessage.success('考核配置已创建')
    showDialog.value = false
    resetForm()
    await loadExams()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  form.value = {
    chapter_id: null, total_questions: 6, choice_count: 2, truefalse_count: 2, essay_count: 2,
    programming_count: 0, time_limit_minutes: 0, knowledge_points: [], evaluation_dimensions: [],
  }
  knowledgeInput.value = ''
  dimensionInput.value = '知识掌握情况,基础概念理解,综合分析能力'
}

async function viewResults(exam) {
  try {
    const res = await getExamResults(exam.id)
    const data = res.data
    // 兼容分页 / 非分页格式
    results.value = Array.isArray(data) ? data : (data.items || [])
    showResults.value = true
  } catch { ElMessage.error('获取成绩失败') }
}

async function handleDelete(examId) {
  try {
    await deleteExamConfig(examId)
    ElMessage.success('考核已删除')
    await loadExams()
  } catch { ElMessage.error('删除失败') }
}
</script>
