<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h2>学生管理</h2>
          <div style="display:flex;gap:8px;">
            <el-upload :auto-upload="false" :show-file-list="false" :on-change="handleImportFile" accept=".csv,.xlsx">
              <el-button type="primary">批量导入 (CSV/Excel)</el-button>
            </el-upload>
            <el-button v-if="importFile" type="success" :loading="importing" @click="doImport">
              导入 {{ importFile.name }}
            </el-button>
          </div>
        </div>

        <el-alert v-if="importResult" :title="importResult.message"
          :type="importResult.errors?.length > 0 ? 'warning' : 'success'"
          closable style="margin-bottom:16px;" @close="importResult = null" />

        <el-table :data="students" stripe v-loading="loading" empty-text="暂无学生">
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="full_name" label="姓名" width="120">
            <template #default="{ row }">{{ row.full_name || '-' }}</template>
          </el-table-column>
          <el-table-column label="完成考核" width="120">
            <template #default="{ row }">{{ row.completed_exams }} / {{ row.total_exams }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                {{ row.status === 'active' ? '正常' : row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="280">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" type="warning" @click="openResetPwd(row)">重置密码</el-button>
              <el-button size="small" @click="showStudentDetail(row)">成绩</el-button>
              <el-popconfirm title="确定移除该学生？" @confirm="handleRemove(row.id)">
                <template #reference>
                  <el-button size="small" type="danger" text>移除</el-button>
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
          @current-change="loadStudents"
          @size-change="loadStudents"
          style="margin-top:16px;justify-content:flex-end;"
        />

        <!-- 编辑弹窗 -->
        <el-dialog v-model="editVisible" title="编辑学生信息" width="400px">
          <el-form :model="editForm" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="editForm.username" />
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="editForm.full_name" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="editVisible = false">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveEdit">确定</el-button>
          </template>
        </el-dialog>

        <!-- 重置密码弹窗 -->
        <el-dialog v-model="pwdVisible" title="重置学生密码" width="400px">
          <el-form :model="pwdForm" label-width="100px">
            <el-form-item label="学生">
              <span>{{ pwdForm.name }}</span>
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwdForm.password" placeholder="默认: 123456" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="pwdVisible = false">取消</el-button>
            <el-button type="warning" :loading="resetting" @click="doResetPwd">确认重置</el-button>
          </template>
        </el-dialog>

        <!-- 成绩弹窗 -->
        <el-dialog v-model="showDetail" :title="selectedStudent?.full_name || selectedStudent?.username" width="600px">
          <el-table :data="studentRecords" stripe v-loading="loadingRecords">
            <el-table-column prop="chapter_title" label="章节" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ r }">
                <el-tag :type="r.status === 'completed' ? 'success' : 'warning'" size="small">
                  {{ r.status === 'completed' ? '已完成' : '进行中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="成绩" width="80">
              <template #default="{ row: r }">{{ r.score != null ? Math.round(r.score) : '-' }}</template>
            </el-table-column>
            <el-table-column prop="completed_at" label="完成时间" width="170">
              <template #default="{ row: r }">{{ formatDate(r.completed_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row: r }">
                <el-button
                  v-if="r.status === 'completed'"
                  size="small" type="primary"
                  @click="viewStudentAnswers(r)"
                >
                  查看答卷
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-dialog>

        <!-- 答卷详情弹窗 -->
        <el-dialog v-model="showAnswers" title="学生答卷详情" width="700px" @close="answersData = null">
          <div v-if="answersData" v-loading="loadingAnswers">
            <div style="margin-bottom:16px;padding:12px;background:#f5f7fa;border-radius:6px;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span><strong>学生：</strong>{{ answersData.student_name || selectedStudent?.full_name || selectedStudent?.username }}</span>
                <span><strong>章节：</strong>{{ answersData.chapter_title || '-' }}</span>
                <span><strong>成绩：</strong>
                  <el-tag :type="answersData.score >= 60 ? 'success' : 'danger'" size="small">
                    {{ answersData.score != null ? Math.round(answersData.score) + '分' : '-' }}
                  </el-tag>
                </span>
              </div>
            </div>

            <div v-for="(q, idx) in (answersData.questions || [])" :key="idx"
              style="margin-bottom:12px;padding:12px;border:1px solid #ebeef5;border-radius:6px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <el-tag :type="getAnswerTypeColor(q.question_type)" size="small">
                  {{ getAnswerTypeLabel(q.question_type) }}
                </el-tag>
                <span style="font-weight:500;">第{{ idx + 1 }}题</span>
                <el-tag v-if="q.is_correct" type="success" size="small">正确</el-tag>
                <el-tag v-else type="danger" size="small">错误</el-tag>
              </div>
              <div style="margin-bottom:6px;white-space:pre-wrap;">{{ q.question_text }}</div>
              <div v-if="q.options && Object.keys(q.options).length > 0" style="margin-bottom:6px;color:#909399;">
                <span v-for="(opt, key) in q.options" :key="key" style="margin-right:16px;">
                  {{ key }}. {{ opt }}
                </span>
              </div>
              <div style="display:flex;gap:24px;margin-top:8px;">
                <span>
                  学生答案：
                  <span :style="{ color: q.is_correct ? '#67C23A' : '#F56C6C', fontWeight: 'bold' }">
                    {{ q.student_answer || '(未作答)' }}
                  </span>
                </span>
                <span v-if="!q.is_correct">
                  正确答案：
                  <span style="color:#67C23A;font-weight:bold;">{{ q.correct_answer }}</span>
                </span>
              </div>
            </div>

            <div v-if="answersData.dimensions && answersData.dimensions.length > 0"
              style="margin-top:16px;padding:12px;background:#f5f7fa;border-radius:6px;">
              <strong>维度评分：</strong>
              <div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;">
                <span v-for="d in answersData.dimensions" :key="d.name">
                  {{ d.name }}：<el-tag size="small">{{ d.score }}分</el-tag>
                </span>
              </div>
            </div>

            <div v-if="answersData.report"
              style="margin-top:16px;padding:12px;background:#fafafa;border-radius:6px;white-space:pre-wrap;">
              <strong>综合评价：</strong>
              <div style="margin-top:8px;color:#606266;">{{ answersData.report }}</div>
            </div>
          </div>
          <template #footer>
            <el-button @click="showAnswers = false">关闭</el-button>
          </template>
        </el-dialog>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import { getStudents, getStudentExams, importStudents, updateStudent, resetStudentPassword, removeStudent, getStudentExamAnswers } from '../../api/teacher'
import { formatDate } from '../../utils/format'
import { ElMessage } from 'element-plus'

const students = ref([])
const loading = ref(false)
const showDetail = ref(false)
const selectedStudent = ref(null)
const studentRecords = ref([])
const loadingRecords = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

// Import
const importFile = ref(null)
const importing = ref(false)
const importResult = ref(null)

// Edit
const editVisible = ref(false)
const editForm = ref({ id: null, username: '', full_name: '' })
const saving = ref(false)

// Reset password
const pwdVisible = ref(false)
const pwdForm = ref({ id: null, name: '', password: '' })
const resetting = ref(false)

// Answer review
const showAnswers = ref(false)
const answersData = ref(null)
const loadingAnswers = ref(false)

onMounted(loadStudents)

async function loadStudents() {
  loading.value = true
  try {
    const res = await getStudents({ page: page.value, page_size: pageSize.value })
    if (Array.isArray(res.data)) {
      students.value = res.data
      total.value = res.data.length
    } else {
      students.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch { /* */ }
  finally { loading.value = false }
}

// Import
function handleImportFile(file) { importFile.value = file.raw; importResult.value = null }
async function doImport() {
  if (!importFile.value) return
  importing.value = true
  try {
    const fd = new FormData(); fd.append('file', importFile.value)
    importResult.value = (await importStudents(fd)).data
    ElMessage.success(importResult.value.message)
    importFile.value = null
    await loadStudents()
  } catch { ElMessage.error('导入失败') }
  finally { importing.value = false }
}

// Edit
function openEdit(row) {
  editForm.value = { id: row.id, username: row.username, full_name: row.full_name || '' }
  editVisible.value = true
}
async function saveEdit() {
  saving.value = true
  try {
    await updateStudent(editForm.value.id, { username: editForm.value.username, full_name: editForm.value.full_name })
    ElMessage.success('已更新')
    editVisible.value = false
    await loadStudents()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '更新失败') }
  finally { saving.value = false }
}

// Reset password
function openResetPwd(row) {
  pwdForm.value = { id: row.id, name: row.full_name || row.username, password: '' }
  pwdVisible.value = true
}
async function doResetPwd() {
  resetting.value = true
  try {
    const res = await resetStudentPassword(pwdForm.value.id, pwdForm.value.password || '123456')
    ElMessage.success(res.data.message)
    pwdVisible.value = false
  } catch (e) { ElMessage.error('操作失败') }
  finally { resetting.value = false }
}

// Remove
async function handleRemove(id) {
  try { await removeStudent(id); ElMessage.success('已移除'); await loadStudents() }
  catch { ElMessage.error('操作失败') }
}

// View scores
async function showStudentDetail(student) {
  selectedStudent.value = student
  loadingRecords.value = true
  showDetail.value = true
  try {
    const res = await getStudentExams(student.id)
    studentRecords.value = Array.isArray(res.data) ? res.data : (res.data.items || [])
  }
  finally { loadingRecords.value = false }
}

// View student answers
async function viewStudentAnswers(record) {
  loadingAnswers.value = true
  showAnswers.value = true
  answersData.value = null
  try {
    const examId = record.exam_config_id
    const studentId = selectedStudent.value.id
    const res = await getStudentExamAnswers(examId, studentId)
    answersData.value = res.data
  } catch (e) {
    ElMessage.error('获取答卷失败')
    showAnswers.value = false
  } finally {
    loadingAnswers.value = false
  }
}

function getAnswerTypeLabel(type) {
  const map = { choice: '选择题', judge: '判断题', short_answer: '简答题', programming: '编程题' }
  return map[type] || type
}

function getAnswerTypeColor(type) {
  const map = { choice: '', judge: 'warning', short_answer: 'success', programming: 'danger' }
  return map[type] || ''
}
</script>
