<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h2>课程资料</h2>
          <el-select v-model="filterChapter" placeholder="按章节筛选" clearable style="width:220px;" @change="loadMaterials">
            <el-option v-for="ch in chapters" :key="ch.id" :label="ch.title" :value="ch.id" />
          </el-select>
        </div>

        <el-table :data="materials" stripe v-loading="loading" empty-text="暂无资料，请联系老师上传">
          <el-table-column prop="file_name" label="文件名" min-width="250">
            <template #default="{ row }">
              <el-icon style="margin-right:6px;"><Document /></el-icon>
              {{ row.file_name }}
            </template>
          </el-table-column>
          <el-table-column prop="file_type" label="类型" width="80" />
          <el-table-column prop="chapter_title" label="所属章节" width="180">
            <template #default="{ row }">{{ row.chapter_title || '-' }}</template>
          </el-table-column>
          <el-table-column prop="uploaded_at" label="上传时间" width="180">
            <template #default="{ row }">{{ formatDate(row.uploaded_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="previewMaterial(row)">预览</el-button>
              <el-button size="small" type="success" @click="viewMaterial(row)">下载</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Preview Dialog -->
        <el-dialog v-model="previewVisible" :title="previewTitle" width="900px" top="3vh" destroy-on-close @close="cleanupPreview">
          <div v-loading="previewLoading" style="min-height:300px;">
            <!-- 图片预览 -->
            <div v-if="previewType === 'image'" style="text-align:center;">
              <img v-if="previewUrl" :src="previewUrl" :alt="previewTitle" style="max-width:100%;max-height:65vh;border-radius:4px;" />
              <el-empty v-else-if="!previewLoading" description="图片加载失败" />
            </div>
            <!-- 文本预览 -->
            <div v-else-if="previewType === 'text'" style="max-height:65vh;overflow:auto;">
              <pre v-if="previewContent" style="white-space:pre-wrap;word-break:break-word;background:#f8fafc;padding:16px;border-radius:8px;font-size:13px;line-height:1.6;margin:0;min-height:200px;">{{ previewContent }}</pre>
              <el-empty v-else-if="!previewLoading" description="暂无内容" />
            </div>
            <!-- PDF 预览 -->
            <div v-else-if="previewType === 'pdf'" style="text-align:center;">
              <iframe v-if="previewUrl" :src="previewUrl" style="width:100%;height:65vh;border:none;border-radius:4px;" />
              <el-empty v-else-if="!previewLoading" description="PDF 加载失败" />
            </div>
            <div v-else style="text-align:center;padding:40px;">
              <el-icon :size="48" style="color:#c0c4cc;"><WarningFilled /></el-icon>
              <p style="color:#909399;">预览加载中...</p>
            </div>
          </div>
          <template #footer>
            <el-button @click="previewVisible = false">关闭</el-button>
            <el-button type="primary" @click="viewMaterial(previewRow)" v-if="previewRow">下载文件</el-button>
          </template>
        </el-dialog>

        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadMaterials"
          @size-change="loadMaterials"
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
import { getStudentMaterials } from '../../api/student'
import { getChapters } from '../../api/teacher'
import { formatDate } from '../../utils/format'
import { ElMessage } from 'element-plus'

const materials = ref([])
const chapters = ref([])
const filterChapter = ref(null)
const loading = ref(false)

// Preview state
const previewVisible = ref(false)
const previewTitle = ref('')
const previewType = ref('')
const previewUrl = ref('')
const previewContent = ref('')
const previewLoading = ref(false)
const previewRow = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

onMounted(async () => {
  await loadMaterials()
  try {
    const res = await getChapters()
    chapters.value = res.data
  } catch { /* ignore */ }
})

async function loadMaterials() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterChapter.value) params.chapter_id = filterChapter.value
    const res = await getStudentMaterials(params)
    if (Array.isArray(res.data)) {
      materials.value = res.data
      total.value = res.data.length
    } else {
      materials.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

async function viewMaterial(row) {
  const url = `/api/v1/student/materials/${row.id}/download`
  const token = localStorage.getItem('token')

  try {
    // 用 fetch 下载文件，避免 Vite proxy 新标签页问题
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('下载失败')

    const blob = await response.blob()
    const blobUrl = URL.createObjectURL(blob)

    // 其他文件触发下载
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = row.file_name
    a.click()
    URL.revokeObjectURL(blobUrl)
  } catch (e) {
    // fetch 失败时回退：直接跳转（如端口不同则用 location.origin）
    window.open(url, '_blank')
  }
}

function getFileExtension(fileType) {
  if (!fileType) return ''
  let ext = fileType.toLowerCase().trim()
  if (!ext.startsWith('.')) ext = '.' + ext
  return ext
}

/** 用 fetch + blob URL 获取需要认证的资源 */
async function fetchBlobUrl(apiUrl, token) {
  const response = await fetch(apiUrl, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  const blob = await response.blob()
  return URL.createObjectURL(blob)
}

function cleanupPreview() {
  if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = ''
  previewContent.value = ''
  previewRow.value = null
}

async function previewMaterial(row) {
  const ext = getFileExtension(row.file_type)
  const apiUrl = `/api/v1/student/materials/${row.id}/download`
  const token = localStorage.getItem('token')

  previewRow.value = row
  previewTitle.value = row.file_name
  previewLoading.value = true
  previewVisible.value = true

  try {
    // PDF: 内嵌 iframe 预览（通过 blob URL 携带认证）
    if (ext === '.pdf') {
      previewType.value = 'pdf'
      previewUrl.value = await fetchBlobUrl(apiUrl, token)
      return
    }

    // 图片: 通过 blob URL 携带认证
    const imageExts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp']
    if (imageExts.includes(ext)) {
      previewType.value = 'image'
      previewUrl.value = await fetchBlobUrl(apiUrl, token)
      return
    }

    // 文本/代码: fetch 文本内容
    const textExts = ['.md', '.txt', '.cpp', '.h', '.hpp', '.c', '.py', '.js', '.json', '.xml', '.yaml', '.yml', '.css', '.html']
    if (textExts.includes(ext)) {
      previewType.value = 'text'
      const response = await fetch(apiUrl, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error('加载失败')
      previewContent.value = await response.text()
      if (!previewContent.value || previewContent.value.trim() === '') {
        previewContent.value = '（文件内容为空）'
      }
      return
    }

    // Office 文档
    const officeExts = ['.pptx', '.ppt', '.docx', '.doc', '.xlsx', '.xls']
    if (officeExts.includes(ext)) {
      previewVisible.value = false
      ElMessage.info('该格式不支持在线预览，请下载查看')
      return
    }

    // 未知格式 → 尝试文本预览
    previewType.value = 'text'
    try {
      const response = await fetch(apiUrl, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (response.ok) {
        previewContent.value = await response.text()
      } else {
        previewVisible.value = false
        viewMaterial(row)
      }
    } catch {
      previewVisible.value = false
      viewMaterial(row)
    }
  } catch (e) {
    // 加载失败
    previewContent.value = ''
    previewUrl.value = ''
    ElMessage.error('文件加载失败: ' + (e.message || '未知错误'))
  } finally {
    previewLoading.value = false
  }
}
</script>
