<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <h2>章节考核</h2>
        <div v-if="!exams.length && !loading" style="text-align:center;padding:60px 0;">
          <el-empty description="暂无考核">
            <template v-if="!myTeacher">
              <p style="color:#909399;margin-bottom:16px;">你还未选择教师，请先选择教师才能查看考核</p>
              <el-button type="primary" @click="showTeacherSelect = true">选择教师</el-button>
            </template>
            <template v-else>
              <p style="color:#909399;">你的教师还没有配置考核，请联系教师</p>
            </template>
          </el-empty>
        </div>

        <el-table v-else :data="exams" stripe style="margin-top:24px;" empty-text="暂无考核">
          <el-table-column prop="chapter_title" label="章节" width="200" />
          <el-table-column prop="total_questions" label="题数" width="80" />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getExamStatusType(row.status)">{{ getExamStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="成绩" width="80">
            <template #default="{ row }">{{ row.score != null ? Math.round(row.score) + '分' : '-' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button
                v-if="row.status !== 'completed'"
                type="primary" size="small"
                @click="startExam(row)"
              >
                {{ row.status === 'in_progress' ? '继续答题' : '开始考核' }}
              </el-button>
              <el-button
                v-if="row.status === 'completed'"
                type="success" size="small"
                @click="viewReport(row)"
              >
                查看报告
              </el-button>
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

        <!-- 教师选择弹窗 -->
        <el-dialog v-model="showTeacherSelect" title="选择教师" width="400px">
          <el-select v-model="selectedTeacherId" placeholder="请选择教师" style="width:100%;">
            <el-option v-for="t in teachers" :key="t.id"
              :label="(t.full_name || t.username) + ' (' + t.username + ')'" :value="t.id" />
          </el-select>
          <template #footer>
            <el-button @click="showTeacherSelect = false">取消</el-button>
            <el-button type="primary" :disabled="!selectedTeacherId" @click="chooseTeacher">确认</el-button>
          </template>
        </el-dialog>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import { getExams } from '../../api/exam'
import { getTeachers, getMyTeacher, selectTeacher } from '../../api/student'
import { getExamStatusText, getExamStatusType } from '../../utils/format'
import { ElMessage } from 'element-plus'

const router = useRouter()
const exams = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const showTeacherSelect = ref(false)
const teachers = ref([])
const myTeacher = ref(null)
const selectedTeacherId = ref(null)

onMounted(async () => {
  await loadExams()
  try { const res = await getMyTeacher(); myTeacher.value = res.data } catch { myTeacher.value = null }
  try { const res = await getTeachers(); teachers.value = res.data } catch {}
})

async function loadExams() {
  loading.value = true
  try {
    const res = await getExams({ page: page.value, page_size: pageSize.value })
    if (Array.isArray(res.data)) {
      exams.value = res.data
      total.value = res.data.length
    } else {
      exams.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch { /* ignore */ }
  finally { loading.value = false }
}

async function chooseTeacher() {
  try {
    await selectTeacher(selectedTeacherId.value)
    const res = await getMyTeacher()
    myTeacher.value = res.data
    showTeacherSelect.value = false
    ElMessage.success('教师选择成功')
    await loadExams()
  } catch { ElMessage.error('选择失败') }
}

function startExam(exam) {
  router.push(`/student/exams/${exam.config_id}`)
}

function viewReport(exam) {
  if (exam.record_id) {
    router.push(`/student/exams/${exam.record_id}/report`)
  }
}
</script>
