import instance from './axios'

export function getStudentMaterials(params = {}) {
  return instance.get('/student/materials', { params })
}

export function getMaterialDownloadUrl(id) {
  return `/api/v1/student/materials/${id}/download`
}

export function getTeachers() {
  return instance.get('/student/teachers')
}

export function selectTeacher(teacherId) {
  return instance.post('/student/teacher', { teacher_id: teacherId })
}

export function getMyTeacher() {
  return instance.get('/student/teacher')
}

export function getWrongAnswers(params = {}) {
  return instance.get('/student/wrong-answers', { params })
}

export function deleteWrongAnswer(id) {
  return instance.delete(`/student/wrong-answers/${id}`)
}
