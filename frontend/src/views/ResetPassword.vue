<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">
          <el-icon :size="32"><Monitor /></el-icon>
        </div>
        <h2>重置密码</h2>
        <p>请设置您的新密码</p>
      </div>
      <el-form :model="form" @submit.prevent="handleResetPassword" class="auth-form">
        <el-form-item>
          <el-input v-model="form.new_password" type="password" placeholder="新密码（至少6位）" size="large" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.confirm_password" type="password" placeholder="确认新密码" size="large" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;">
          重置密码
        </el-button>
      </el-form>
      <div class="auth-footer">
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { resetPassword } from '../api/auth'
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const form = ref({ new_password: '', confirm_password: '' })

async function handleResetPassword() {
  if (!form.value.new_password) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (form.value.new_password.length < 6) {
    ElMessage.warning('密码至少需要6位')
    return
  }
  if (form.value.new_password !== form.value.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  const token = route.query.token
  if (!token) {
    ElMessage.error('缺少重置令牌，请从邮件链接重新访问')
    return
  }

  loading.value = true
  try {
    await resetPassword({ token, new_password: form.value.new_password })
    ElMessage.success('密码重置成功，请重新登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '重置失败，请稍后重试')
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
.auth-footer { text-align: center; margin-top: 20px; font-size: 14px; color: #94a3b8; }
.auth-footer a { color: #6366f1; text-decoration: none; font-weight: 500; }
</style>
