<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">
          <el-icon :size="32"><Monitor /></el-icon>
        </div>
        <h2>创建账号</h2>
        <p>加入 C++ 课程智能体平台</p>
      </div>
      <el-form :model="form" @submit.prevent="handleRegister" class="auth-form">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名 (3-50位字母数字)" size="large" :prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码 (至少6位)" size="large" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-radio-group v-model="form.role" style="width:100%;">
            <el-radio-button value="student" style="width:50%;">学生</el-radio-button>
            <el-radio-button value="teacher" style="width:50%;">教师</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.full_name" placeholder="真实姓名 (选填)" size="large" :prefix-icon="UserFilled" />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;">
          注 册
        </el-button>
      </el-form>
      <div class="auth-footer">
        已有账号？<router-link to="/login">去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const form = ref({ username: '', password: '', role: 'student', full_name: '' })

async function handleRegister() {
  loading.value = true
  try {
    await userStore.registerAction(form.value)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.auth-card { width: 420px; background: #fff; border-radius: 16px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,.15); }
.auth-header { text-align: center; margin-bottom: 32px; }
.auth-icon { width: 64px; height: 64px; margin: 0 auto 16px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; display: flex; align-items: center; justify-content: center; color: #fff; }
.auth-header h2 { font-size: 22px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.auth-header p { font-size: 14px; color: #94a3b8; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 14px; color: #94a3b8; }
.auth-footer a { color: #6366f1; text-decoration: none; font-weight: 500; }
</style>
