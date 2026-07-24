<template>
  <div class="sidebar">
    <!-- Logo -->
    <div class="logo">
      <el-icon :size="24"><Monitor /></el-icon>
      <span>C++ 智能体</span>
    </div>

    <!-- 搜索 -->
    <div class="search-wrap">
      <el-input
        v-model="keyword"
        placeholder="搜索..."
        :prefix-icon="Search"
        size="default"
        class="search-input"
        @keyup.enter="handleSearch"
        clearable
      />
    </div>

    <!-- 导航菜单 -->
    <div class="menu-section">
      <template v-if="role === 'student'">
        <div class="section-title">学习</div>
        <router-link to="/student/dashboard" class="menu-item" active-class="active">
          <el-icon><DataAnalysis /></el-icon><span>学习仪表盘</span>
        </router-link>
        <router-link to="/student/home" class="menu-item" active-class="active">
          <el-icon><ChatDotRound /></el-icon><span>AI 对话</span>
        </router-link>
        <router-link to="/student/materials" class="menu-item" active-class="active">
          <el-icon><FolderOpened /></el-icon><span>课程资料</span>
        </router-link>
        <router-link to="/student/cpp-runner" class="menu-item" active-class="active">
          <el-icon><Monitor /></el-icon><span>在线编程</span>
        </router-link>

        <div class="section-title">考核</div>
        <router-link to="/student/exams" class="menu-item" active-class="active">
          <el-icon><Edit /></el-icon><span>章节考核</span>
        </router-link>
        <router-link to="/student/wrong-answers" class="menu-item" active-class="active">
          <el-icon><Collection /></el-icon><span>错题本</span>
        </router-link>
      </template>

      <template v-else-if="role === 'teacher'">
        <div class="section-title">教学</div>
        <router-link to="/teacher/dashboard" class="menu-item" active-class="active">
          <el-icon><DataAnalysis /></el-icon><span>教学仪表盘</span>
        </router-link>
        <router-link to="/teacher/home" class="menu-item" active-class="active">
          <el-icon><Upload /></el-icon><span>资料上传</span>
        </router-link>
        <router-link to="/teacher/exams" class="menu-item" active-class="active">
          <el-icon><Edit /></el-icon><span>考核配置</span>
        </router-link>

        <div class="section-title">管理</div>
        <router-link to="/teacher/students" class="menu-item" active-class="active">
          <el-icon><User /></el-icon><span>学生管理</span>
        </router-link>
        <router-link to="/teacher/model-config" class="menu-item" active-class="active">
          <el-icon><Setting /></el-icon><span>模型配置</span>
        </router-link>
      </template>
    </div>

    <!-- 底部用户信息 -->
    <div class="sidebar-footer">
      <el-dropdown trigger="click" placement="top-start">
        <div class="user-card">
          <el-avatar :size="36" style="background:#6366f1;font-size:14px;font-weight:700;">{{ avatarText }}</el-avatar>
          <div class="user-info">
            <div class="user-name">{{ user?.full_name || user?.username }}</div>
            <div class="user-role">{{ role === 'teacher' ? '教师' : '学生' }}</div>
          </div>
          <el-icon style="color:#94a3b8;"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>
              <router-link to="/profile" style="text-decoration:none;color:inherit;display:block;">👤 个人中心</router-link>
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.user)
const role = computed(() => userStore.user?.role)

const keyword = ref('')

const avatarText = computed(() => {
  const name = user.value?.full_name || user.value?.username || '?'
  return name.slice(0, 2).toUpperCase()
})

function handleSearch() {
  const q = keyword.value.trim()
  if (q) {
    router.push({ path: '/search', query: { q } })
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 220px; height: 100vh;
  background: #1e293b;
  display: flex; flex-direction: column;
  user-select: none;
}
.logo {
  display: flex; align-items: center; gap: 10px;
  padding: 18px 16px 12px;
  color: #fff; font-size: 17px; font-weight: 700;
  letter-spacing: .5px;
}

/* 搜索 */
.search-wrap {
  padding: 0 12px 8px;
}
.search-wrap :deep(.el-input__wrapper) {
  border-radius: 8px;
  background: rgba(255,255,255,.1);
  border: none; box-shadow: none;
}
.search-wrap :deep(.el-input__wrapper:hover) {
  background: rgba(255,255,255,.15);
}
.search-wrap :deep(.el-input__wrapper.is-focus) {
  background: rgba(255,255,255,.2);
  box-shadow: 0 0 0 1px rgba(255,255,255,.3);
}
.search-wrap :deep(.el-input) {
  color: #fff;
}
.search-wrap :deep(.el-input__inner) {
  color: #e2e8f0;
}
.search-wrap :deep(.el-input__inner::placeholder) {
  color: #94a3b8;
}
.search-wrap :deep(.el-input__prefix) {
  color: #94a3b8;
}

.section-title {
  font-size: 11px; color: #64748b; text-transform: uppercase;
  letter-spacing: 1px; padding: 16px 20px 6px; font-weight: 600;
}
.menu-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; margin: 2px 8px; border-radius: 8px;
  color: #cbd5e1; text-decoration: none; font-size: 14px;
  transition: all .15s;
}
.menu-item:hover { background: rgba(255,255,255,.08); color: #fff; }
.menu-item.active { background: #6366f1; color: #fff; font-weight: 500; }

/* 底部用户卡片 */
.sidebar-footer {
  margin-top: auto;
  padding: 10px;
  border-top: 1px solid rgba(255,255,255,.08);
}
.user-card {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px; border-radius: 10px;
  cursor: pointer; transition: background .15s;
}
.user-card:hover { background: rgba(255,255,255,.08); }
.user-info { flex: 1; overflow: hidden; }
.user-name {
  font-size: 13px; font-weight: 500; color: #f1f5f9;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.user-role {
  font-size: 11px; color: #94a3b8;
}
</style>
