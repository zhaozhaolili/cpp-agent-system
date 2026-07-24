import { createRouter, createWebHistory } from 'vue-router'

// Public
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import ForgotPassword from '../views/ForgotPassword.vue'
import ResetPassword from '../views/ResetPassword.vue'
import SearchResults from '../views/SearchResults.vue'
import Profile from '../views/Profile.vue'

// Student
import StudentHome from '../views/student/Chat.vue'
import StudentMaterials from '../views/student/Materials.vue'
import StudentExamList from '../views/student/ExamList.vue'
import StudentExamRoom from '../views/student/ExamRoom.vue'
import StudentExamReport from '../views/student/ExamReport.vue'
import StudentWrongAnswers from '../views/student/WrongAnswers.vue'
import StudentCppRunner from '../views/student/CppRunner.vue'
import StudentDashboard from '../views/student/Dashboard.vue'

// Teacher
import TeacherHome from '../views/teacher/Upload.vue'
import TeacherMaterials from '../views/teacher/Upload.vue'
import TeacherExamConfig from '../views/teacher/ExamConfig.vue'
import TeacherStudents from '../views/teacher/StudentsList.vue'
import TeacherModelConfig from '../views/teacher/ModelConfig.vue'
import TeacherDashboard from '../views/teacher/Dashboard.vue'

const routes = [
  // Public
  { path: '/', component: Home, meta: { requiresAuth: false } },
  { path: '/login', component: Login, meta: { requiresAuth: false } },
  { path: '/register', component: Register, meta: { requiresAuth: false } },
  { path: '/forgot-password', component: ForgotPassword, meta: { requiresAuth: false } },
  { path: '/reset-password', component: ResetPassword, meta: { requiresAuth: false } },
  { path: '/search', component: SearchResults, meta: { requiresAuth: true } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },

  // Student routes
  {
    path: '/student/home',
    component: StudentHome,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/materials',
    component: StudentMaterials,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/exams',
    component: StudentExamList,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/exams/:id',
    component: StudentExamRoom,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/exams/:id/report',
    component: StudentExamReport,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/wrong-answers',
    component: StudentWrongAnswers,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/cpp-runner',
    component: StudentCppRunner,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/dashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'student' }
  },

  // Teacher routes
  {
    path: '/teacher/home',
    component: TeacherHome,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/materials',
    component: TeacherMaterials,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/exams',
    component: TeacherExamConfig,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/students',
    component: TeacherStudents,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/model-config',
    component: TeacherModelConfig,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/dashboard',
    component: TeacherDashboard,
    meta: { requiresAuth: true, role: 'teacher' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null

  if (to.meta.requiresAuth) {
    if (!token) {
      return '/login'
    }
    if (to.meta.role && user?.role !== to.meta.role) {
      return '/login'
    }
    return true
  }

  // 已登录用户访问登录/注册页 → 跳转到首页
  if (token && (to.path === '/login' || to.path === '/register')) {
    const role = user?.role || 'student'
    return role === 'teacher' ? '/teacher/home' : '/student/home'
  }
  return true
})

export default router
