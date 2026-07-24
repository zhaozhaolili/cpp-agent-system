/**
 * 鉴权逻辑 composable
 */
import { computed } from 'vue'
import { useUserStore } from '../stores/user'

export function useAuth() {
  const userStore = useUserStore()
  const isLoggedIn = computed(() => !!userStore.token)
  const currentUser = computed(() => userStore.user)
  const isTeacher = computed(() => userStore.user?.role === 'teacher')
  const isStudent = computed(() => userStore.user?.role === 'student')

  return { isLoggedIn, currentUser, isTeacher, isStudent, userStore }
}
