import instance from './axios'

export const search = (params) => instance.get('/search', { params })
