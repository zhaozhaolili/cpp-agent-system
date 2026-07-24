import instance from './axios'

export const register = (data) => {
    return instance.post('/auth/register', data)
}

export const login = (data) => {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    return instance.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
}

export const getMe = () => {
    return instance.get('/auth/me')
}

export const updateProfile = (data) => {
    return instance.put('/auth/profile', data)
}

export const forgotPassword = (data) => instance.post('/auth/forgot-password', data)

export const resetPassword = (data) => instance.post('/auth/reset-password', data)