<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">
          <el-icon :size="32"><Monitor /></el-icon>
        </div>
        <h2>忘记密码</h2>
        <p>输入邮箱地址，我们将发送重置链接</p>
      </div>
      <el-form :model="form" @submit.prevent="handleForgotPassword" class="auth-form">
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱地址" size="large" :prefix-icon="Message" />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;">
          发送重置链接
        </el-button>
      </el-form>
      <div v-if="success" class="auth-success">
        <el-alert type="success" :closable="false" show-icon>
          重置密码链接已发送到您的邮箱，请查收邮件并按提示操作。
        </el-alert>
      </div>
      <div class="auth-footer">
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { forgotPassword } from '../api/auth'
import { ElMessage } from 'element-plus'
import { Message } from '@element-plus/icons-vue'

const loading = ref(false)
const success = ref(false)
const form = ref({ email: '' })

async function handleForgotPassword() {
  if (!form.value.email) {
    ElMessage.warning('请输入邮箱地址')
    return
  }
  loading.value = true
  try {
    await forgotPassword({ email: form.value.email })
    success.value = true
    ElMessage.success('重置链接已发送')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发送失败，请稍后重试')
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.auth-card { width: 400px; background: #fff; border-radius: 16px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,.15); }
.auth-header { text-align: center; margin-bottom: 32px; }
.auth-icon { width: 64px; height: 64px; margin: 0 auto 16px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; display: flex; align-items: center; justify-content: center; color: #fff; }
.auth-header h2 { font-size: 22px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.auth-header p { font-size: 14px; color: #94a3b8; }
.auth-success { margin-bottom: 20px; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 14px; color: #94a3b8; }
.auth-footer a { color: #6366f1; text-decoration: none; font-weight: 500; }
</style>
