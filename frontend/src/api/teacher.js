import instance from './axios'

export function uploadMaterial(formData, onProgress) {
  return instance.post('/teacher/materials/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        onProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total))
      }
    },
  })
}

export function getMaterials(params = {}) {
  return instance.get('/teacher/materials', { params })
}

export function deleteMaterial(id) {
  return instance.delete(`/teacher/materials/${id}`)
}

export function getStudents(params = {}) {
  return instance.get('/teacher/students', { params })
}

export function getStudentExams(studentId) {
  return instance.get(`/teacher/students/${studentId}/exams`)
}

export function getChapters() {
  return instance.get('/teacher/chapters')
}

export function getModelConfig() {
  return instance.get('/teacher/model-config')
}

export function updateModelConfig(data) {
  return instance.put('/teacher/model-config', data)
}

export function getTeacherStats() {
  return instance.get('/teacher/stats')
}

export function importStudents(formData) {
  return instance.post('/teacher/students/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function updateStudent(studentId, data) {
  return instance.put(`/teacher/students/${studentId}`, data)
}

export function resetStudentPassword(studentId, newPassword) {
  return instance.post(`/teacher/students/${studentId}/reset-password`, { new_password: newPassword })
}

export function removeStudent(studentId) {
  return instance.delete(`/teacher/students/${studentId}`)
}

export function batchDeleteMaterials(materialIds) {
  return instance.post('/teacher/materials/batch-delete', { material_ids: materialIds })
}

export function getStudentExamAnswers(examId, studentId) {
  return instance.get(`/teacher/exams/${examId}/student/${studentId}/answers`)
}
