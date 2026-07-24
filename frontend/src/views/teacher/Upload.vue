<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h2>资料管理</h2>
          <div style="display:flex;align-items:center;gap:8px;">
            <el-select v-model="uploadChapterId" placeholder="选择章节" style="width:200px;">
              <el-option v-for="ch in chapters" :key="ch.id" :label="ch.title" :value="ch.id" />
            </el-select>
            <el-upload
              drag
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleFileSelect"
              accept=".pdf,.pptx,.ppt,.docx,.doc,.md,.txt,.cpp,.h,.hpp"
              class="upload-drag-zone"
            >
              <el-icon style="font-size:40px;color:#409EFF;"><UploadFilled /></el-icon>
              <div class="el-upload__text" style="margin-top:8px;">
                将文件拖到此处，或<em>点击上传</em>
              </div>
            </el-upload>
            <el-button
              v-if="selectedFile"
              type="success"
              :loading="uploading"
              @click="uploadFile"
            >
              上传 {{ selectedFile.name }}
            </el-button>
          </div>
        </div>

        <el-progress
          v-if="uploading"
          :percentage="uploadPercent"
          :stroke-width="8"
          style="margin-bottom:12px;"
        />

        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <el-button
            type="danger"
            :disabled="selectedRows.length === 0"
            @click="batchDelete"
          >
            批量删除 ({{ selectedRows.length }})
          </el-button>
        </div>

        <el-table :data="materials" stripe v-loading="loading" empty-text="暂无资料"
          @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="file_name" label="文件名" min-width="250" />
          <el-table-column prop="file_type" label="类型" width="80" />
          <el-table-column prop="chapter_title" label="所属章节" width="180">
            <template #default="{ row }">{{ row.chapter_title || '-' }}</template>
          </el-table-column>
          <el-table-column prop="uploaded_at" label="上传时间" width="180">
            <template #default="{ row }">{{ formatDate(row.uploaded_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-popconfirm title="确认删除？" @confirm="deleteMaterial(row.id)">
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
import { getMaterials, uploadMaterial, deleteMaterial as apiDeleteMaterial, getChapters, batchDeleteMaterials } from '../../api/teacher'
import { formatDate } from '../../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const materials = ref([])
const chapters = ref([])
const loading = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)
const uploadChapterId = ref(null)
const uploadPercent = ref(0)
const selectedRows = ref([])
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
    const res = await getMaterials({ page: page.value, page_size: pageSize.value })
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

function handleFileSelect(file) {
  selectedFile.value = file.raw
}

async function uploadFile() {
  if (!selectedFile.value) return
  uploading.value = true
  uploadPercent.value = 0
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    if (uploadChapterId.value) {
      fd.append('chapter_id', uploadChapterId.value)
    }
    await uploadMaterial(fd, (pct) => {
      uploadPercent.value = pct
    })
    ElMessage.success('上传成功')
    selectedFile.value = null
    await loadMaterials()
  } catch (e) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

function handleSelectionChange(rows) {
  selectedRows.value = rows
}

async function batchDelete() {
  if (selectedRows.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确认删除选中的 ${selectedRows.value.length} 个资料？`,
      '批量删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    const ids = selectedRows.value.map(r => r.id)
    await batchDeleteMaterials(ids)
    ElMessage.success('已删除')
    selectedRows.value = []
    await loadMaterials()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('批量删除失败')
  }
}

async function deleteMaterial(id) {
  try {
    await apiDeleteMaterial(id)
    ElMessage.success('已删除')
    await loadMaterials()
  } catch { ElMessage.error('删除失败') }
}
</script>

<style scoped>
.upload-drag-zone :deep(.el-upload-dragger) {
  padding: 16px 24px;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  transition: border-color 0.3s;
}
.upload-drag-zone :deep(.el-upload-dragger:hover) {
  border-color: #409EFF;
}
</style>
