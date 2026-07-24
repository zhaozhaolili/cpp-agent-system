import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, register, getMe } from '../api/auth'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)
    const token = ref(localStorage.getItem('token') || '')

    const setToken = (newToken) => {
        token.value = newToken
        localStorage.setItem('token', newToken)
    }

    const clearToken = () => {
        token.value = ''
        localStorage.removeItem('token')
    }

    const loginAction = async (credentials) => {
        const res = await login(credentials)
        setToken(res.data.access_token)
        await fetchUser()
        return res
    }

    const registerAction = async (userData) => {
        const res = await register(userData)
        return res
    }

    const fetchUser = async () => {
        if (!token.value) return
        try {
            const res = await getMe()
            user.value = res.data
            localStorage.setItem('user', JSON.stringify(res.data))
        } catch (e) {
            clearToken()
            user.value = null
            localStorage.removeItem('user')
        }
    }

    const logout = () => {
        clearToken()
        user.value = null
        localStorage.removeItem('user')
    }

    // 初始化时自动获取用户（如果有token）
    if (token.value) {
        fetchUser()
    }

    return { user, token, loginAction, registerAction, fetchUser, logout }
})