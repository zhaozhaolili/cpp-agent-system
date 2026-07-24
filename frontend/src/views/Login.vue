<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">
          <el-icon :size="32"><Monitor /></el-icon>
        </div>
        <h2>C++ 课程智能体</h2>
        <p>登录您的账号</p>
      </div>
      <el-form :model="form" @submit.prevent="handleLogin" class="auth-form">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password :prefix-icon="Lock" />
        </el-form-item>
        <div style="text-align:right;margin-bottom:12px;">
          <router-link to="/forgot-password" style="font-size:13px;color:#6366f1;text-decoration:none;">忘记密码？</router-link>
        </div>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;">
          登 录
        </el-button>
      </el-form>
      <div class="auth-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  loading.value = true
  try {
    await userStore.loginAction(form.value)
    ElMessage.success('登录成功')
    router.push(userStore.user?.role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
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
