<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <h2>大模型配置</h2>
        <el-card style="max-width:600px;margin-top:16px;">
          <el-form :model="form" label-width="120px">
            <el-form-item label="当前模型">
              <el-tag type="primary">{{ currentConfig.model }}</el-tag>
            </el-form-item>
            <el-form-item label="API 地址">
              <el-input v-model="currentConfig.base_url" disabled />
            </el-form-item>
            <el-form-item label="API Key">
              <el-input v-model="currentConfig.api_key_masked" disabled />
            </el-form-item>
            <el-form-item label="Embedding 模型">
              <el-input v-model="currentConfig.embedding_model" disabled />
            </el-form-item>
          </el-form>

          <el-divider>修改配置（运行时生效，重启后恢复 .env 值）</el-divider>

          <el-form :model="form" label-width="100px">
            <el-form-item label="API Key">
              <el-input v-model="form.api_key" placeholder="留空则不修改" type="password" show-password />
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input v-model="form.base_url" placeholder="留空则不修改" />
            </el-form-item>
            <el-form-item label="模型">
              <el-input v-model="form.model" placeholder="如 deepseek-chat" />
            </el-form-item>
            <el-form-item label="Embedding 模型">
              <el-input v-model="form.embedding_model" placeholder="如 text-embedding-ada-002" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import { getModelConfig, updateModelConfig } from '../../api/teacher'
import { ElMessage } from 'element-plus'

const currentConfig = ref({
  api_key_masked: '****',
  base_url: '',
  model: '',
  embedding_model: '',
})

const form = ref({
  api_key: '',
  base_url: '',
  model: '',
  embedding_model: '',
})

const saving = ref(false)

onMounted(async () => {
  try {
    const res = await getModelConfig()
    currentConfig.value = res.data
  } catch { /* ignore */ }
})

async function saveConfig() {
  saving.value = true
  try {
    const data = {}
    if (form.value.api_key) data.api_key = form.value.api_key
    if (form.value.base_url) data.base_url = form.value.base_url
    if (form.value.model) data.model = form.value.model
    if (form.value.embedding_model) data.embedding_model = form.value.embedding_model
    await updateModelConfig(data)
    ElMessage.success('配置已保存（运行时生效）')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>
