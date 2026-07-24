<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main style="background:#f5f7fa;">
        <div style="max-width:800px;margin:0 auto;">

          <!-- 用户概览卡片 -->
          <div class="profile-banner">
            <div class="banner-bg"></div>
            <div class="banner-content">
              <el-avatar :size="64" style="background:linear-gradient(135deg,#6366f1,#8b5cf6);font-size:24px;font-weight:700;">
                {{ avatarText }}
              </el-avatar>
              <div class="banner-info">
                <h2>{{ user?.full_name || user?.username }}</h2>
                <div class="banner-meta">
                  <el-tag :type="user?.role==='teacher'?'warning':''" size="small" effect="plain">
                    {{ user?.role === 'teacher' ? '教师' : '学生' }}
                  </el-tag>
                  <span>账号 ID: {{ user?.id }}</span>
                  <span>注册于 {{ formatDate(user?.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab 切换 -->
          <el-card style="border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.04);">
            <el-tabs v-model="activeTab" class="profile-tabs">
              <!-- 个人信息 -->
              <el-tab-pane label="个人信息" name="info">
                <el-form :model="info" label-width="90px" label-position="left" style="max-width:480px;">
                  <el-form-item label="用户名">
                    <el-input v-model="info.username" placeholder="3-50位字母数字" />
                  </el-form-item>
                  <el-form-item label="真实姓名">
                    <el-input v-model="info.full_name" placeholder="真实姓名" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" :loading="savingInfo" @click="saveInfo">保存修改</el-button>
                  </el-form-item>
                </el-form>
              </el-tab-pane>

              <!-- 修改密码 -->
              <el-tab-pane label="修改密码" name="password">
                <el-form :model="pwd" label-width="100px" label-position="left" style="max-width:480px;">
                  <el-form-item label="当前密码">
                    <el-input v-model="pwd.current" type="password" show-password placeholder="输入当前密码" />
                  </el-form-item>
                  <el-form-item label="新密码">
                    <el-input v-model="pwd.newPass" type="password" show-password placeholder="至少6位" />
                  </el-form-item>
                  <el-form-item label="确认密码">
                    <el-input v-model="pwd.confirm" type="password" show-password placeholder="再次输入新密码" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="warning" :loading="savingPwd" @click="savePassword">修改密码</el-button>
                  </el-form-item>
                </el-form>
              </el-tab-pane>

              <!-- 系统设置 -->
              <el-tab-pane label="系统设置" name="settings">
                <div style="max-width:480px;">
                  <div class="setting-item">
                    <div class="setting-label">
                      <span>界面语言</span>
                      <small>系统显示语言</small>
                    </div>
                    <el-select v-model="settings.locale" style="width:140px;">
                      <el-option label="简体中文" value="zh-CN" />
                      <el-option label="English" value="en-US" />
                    </el-select>
                  </div>
                  <div class="setting-item">
                    <div class="setting-label">
                      <span>消息通知</span>
                      <small>开启考核提醒和资料更新通知</small>
                    </div>
                    <el-switch v-model="settings.notification" />
                  </div>
                  <div class="setting-item">
                    <div class="setting-label">
                      <span>自动保存考试</span>
                      <small>答题时自动保存进度</small>
                    </div>
                    <el-switch v-model="settings.autoSaveExam" />
                  </div>
                  <div class="setting-item">
                    <div class="setting-label">
                      <span>代码编辑器主题</span>
                      <small>在线编程运行时的编辑器配色</small>
                    </div>
                    <el-select v-model="settings.codeTheme" style="width:140px;">
                      <el-option label="VS Dark" value="vs-dark" />
                      <el-option label="VS Light" value="vs-light" />
                      <el-option label="Monokai" value="monokai" />
                    </el-select>
                  </div>
                  <div style="margin-top:24px;">
                    <el-button type="primary" @click="saveSettings">保存设置</el-button>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>

        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppHeader from '../components/common/AppHeader.vue'
import AppSidebar from '../components/common/AppSidebar.vue'
import { useUserStore } from '../stores/user'
import { getMe, updateProfile } from '../api/auth'
import { ElMessage } from 'element-plus'
import { formatDate } from '../utils/format'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const activeTab = ref('info')
const savingInfo = ref(false)
const savingPwd = ref(false)

const info = ref({ username: '', full_name: '' })
const pwd = ref({ current: '', newPass: '', confirm: '' })

const settings = ref({
  locale: 'zh-CN',
  notification: true,
  autoSaveExam: true,
  codeTheme: 'vs-dark'
})

const avatarText = computed(() => {
  const name = user.value?.full_name || user.value?.username || '?'
  return name.slice(0, 2).toUpperCase()
})

onMounted(async () => {
  try {
    const res = await getMe()
    info.value.username = res.data.username || ''
    info.value.full_name = res.data.full_name || ''
  } catch { /* */ }

  // 从 localStorage 加载设置
  const saved = localStorage.getItem('app-settings')
  if (saved) {
    try { Object.assign(settings.value, JSON.parse(saved)) } catch {}
  }
})

async function saveInfo() {
  savingInfo.value = true
  try {
    const res = await updateProfile({ username: info.value.username, full_name: info.value.full_name })
    userStore.user = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
    ElMessage.success('个人信息已更新')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally { savingInfo.value = false }
}

async function savePassword() {
  if (!pwd.value.current) return ElMessage.warning('请输入当前密码')
  if (!pwd.value.newPass || pwd.value.newPass.length < 6) return ElMessage.warning('新密码至少6位')
  if (pwd.value.newPass !== pwd.value.confirm) return ElMessage.warning('两次输入的新密码不一致')

  savingPwd.value = true
  try {
    await updateProfile({ current_password: pwd.value.current, new_password: pwd.value.newPass })
    ElMessage.success('密码修改成功，请重新登录')
    pwd.value = { current: '', newPass: '', confirm: '' }
    userStore.logout()
    window.location.href = '/login'
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '修改失败')
  } finally { savingPwd.value = false }
}

function saveSettings() {
  localStorage.setItem('app-settings', JSON.stringify(settings.value))
  ElMessage.success('设置已保存')
}
</script>

<style scoped>
.profile-banner {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.banner-bg {
  height: 80px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
}
.banner-content {
  display: flex; align-items: center; gap: 20px;
  padding: 0 28px 24px;
  margin-top: -32px;
}
.banner-info h2 {
  margin: 0 0 6px;
  font-size: 20px; font-weight: 700; color: #1e293b;
}
.banner-meta {
  display: flex; align-items: center; gap: 16px;
  font-size: 13px; color: #94a3b8;
}
.profile-tabs :deep(.el-tabs__header) {
  margin-bottom: 8px;
}
.setting-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid #f1f5f9;
}
.setting-label span {
  display: block; font-size: 14px; font-weight: 500; color: #334155;
}
.setting-label small {
  display: block; font-size: 12px; color: #94a3b8; margin-top: 2px;
}
</style>
