<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <div class="search-header">
          <el-input
            v-model="query"
            placeholder="搜索对话、资料、错题..."
            size="large"
            :prefix-icon="Search"
            clearable
            @keyup.enter="doSearch"
            style="max-width:500px;"
          />
          <el-button type="primary" size="large" @click="doSearch" style="margin-left:12px;">搜索</el-button>
        </div>

        <el-tabs v-model="scope" @tab-change="onScopeChange" style="margin-top:24px;">
          <el-tab-pane label="全部" name="all" />
          <el-tab-pane label="对话记录" name="chats" />
          <el-tab-pane label="课程资料" name="materials" />
          <el-tab-pane label="错题本" name="wrong_answers" />
          <el-tab-pane v-if="isTeacher" label="学生" name="students" />
        </el-tabs>

        <div v-loading="loading" style="min-height:200px;">
          <div v-if="!loading && results.length === 0 && searched" class="empty-result">
            <el-empty description="未找到相关结果" />
          </div>

          <!-- Student results (teachers only) -->
          <div v-if="scope === 'students' && isTeacher">
            <div v-for="item in results" :key="item.id" class="result-item" @click="goToStudent(item)">
              <el-avatar :size="36" style="background:#6366f1;margin-right:12px;">{{ (item.full_name || item.username || '?').slice(0,2).toUpperCase() }}</el-avatar>
              <div class="result-info">
                <div class="result-title">{{ item.full_name || item.username }}</div>
                <div class="result-desc">{{ item.username }} · {{ item.email || '无邮箱' }}</div>
              </div>
            </div>
          </div>

          <!-- Chat results -->
          <div v-if="scope === 'chats' || scope === 'all'">
            <div v-for="item in filterByType('chat')" :key="item.id" class="result-item" @click="goToChat(item)">
              <el-icon :size="20" style="margin-right:12px;color:#6366f1;"><ChatDotRound /></el-icon>
              <div class="result-info">
                <div class="result-title" v-html="highlight(item.title || item.content?.slice(0, 60) || '对话记录')" />
                <div class="result-desc">{{ item.content?.slice(0, 150) || '' }}</div>
                <div class="result-meta">{{ formatDate(item.created_at) }}</div>
              </div>
            </div>
          </div>

          <!-- Material results -->
          <div v-if="scope === 'materials' || scope === 'all'">
            <div v-for="item in filterByType('material')" :key="item.id" class="result-item" @click="goToMaterials()">
              <el-icon :size="20" style="margin-right:12px;color:#6366f1;"><Document /></el-icon>
              <div class="result-info">
                <div class="result-title" v-html="highlight(item.file_name || item.title || '')" />
                <div class="result-desc">章节: {{ item.chapter_title || '-' }} · 类型: {{ item.file_type || '-' }}</div>
                <div class="result-meta">{{ formatDate(item.uploaded_at || item.created_at) }}</div>
              </div>
            </div>
          </div>

          <!-- Wrong answer results -->
          <div v-if="scope === 'wrong_answers' || scope === 'all'">
            <div v-for="item in filterByType('wrong_answer')" :key="item.id" class="result-item" @click="goToWrongAnswers()">
              <el-icon :size="20" style="margin-right:12px;color:#e2a308;"><WarningFilled /></el-icon>
              <div class="result-info">
                <div class="result-title" v-html="highlight(item.question_text || item.title || '错题')" />
                <div class="result-desc">{{ item.your_answer ? `你的答案: ${item.your_answer}` : '' }} {{ item.correct_answer ? `正确答案: ${item.correct_answer}` : '' }}</div>
                <div class="result-meta">{{ formatDate(item.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="total > 0" style="margin-top:24px;display:flex;justify-content:center;">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            @current-change="doSearch"
          />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { search as searchApi } from '../api/search'
import { useUserStore } from '../stores/user'
import AppHeader from '../components/common/AppHeader.vue'
import AppSidebar from '../components/common/AppSidebar.vue'
import { formatDate } from '../utils/format'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const query = ref('')
const scope = ref('all')
const results = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const searched = ref(false)

const isTeacher = computed(() => userStore.user?.role === 'teacher')

onMounted(() => {
  if (route.query.q) {
    query.value = route.query.q
    doSearch()
  }
})

watch(() => route.query.q, (newVal) => {
  if (newVal) {
    query.value = newVal
    page.value = 1
    doSearch()
  }
})

async function doSearch() {
  const q = query.value.trim()
  if (!q) return

  loading.value = true
  searched.value = true
  try {
    const res = await searchApi({
      q,
      scope: scope.value,
      page: page.value,
      page_size: pageSize.value
    })
    if (res.data) {
      results.value = res.data.items || res.data.results || res.data || []
      total.value = res.data.total || 0
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '搜索失败')
    results.value = []
    total.value = 0
  } finally { loading.value = false }
}

function onScopeChange() {
  page.value = 1
  doSearch()
}

function filterByType(type) {
  if (scope.value !== 'all' && scope.value !== 'students') {
    // When scope is specific, all results belong to that scope
    return scope.value === type || scope.value === type + 's' ? results.value : []
  }
  return results.value.filter(r => r.type === type || r.result_type === type)
}

function highlight(text) {
  if (!text || !query.value) return text || ''
  const escaped = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

function goToChat(item) {
  router.push('/student/home')
}

function goToMaterials() {
  router.push('/student/materials')
}

function goToWrongAnswers() {
  router.push('/student/wrong-answers')
}

function goToStudent(item) {
  router.push('/teacher/students')
}
</script>

<style scoped>
.search-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
}
.result-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: background .15s;
  border-bottom: 1px solid #f1f5f9;
}
.result-item:hover {
  background: #f8fafc;
}
.result-info {
  flex: 1;
}
.result-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}
.result-title :deep(mark) {
  background: #fde68a;
  padding: 0 2px;
  border-radius: 2px;
}
.result-desc {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.result-meta {
  font-size: 12px;
  color: #94a3b8;
}
.empty-result {
  padding: 60px 0;
}
</style>
