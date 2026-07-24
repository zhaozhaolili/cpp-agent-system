import instance from './axios'

export function getExams(params = {}) {
  return instance.get('/student/exams', { params })
}

export function startExam(configId) {
  return instance.post(`/student/exams/${configId}/start`)
}

export function submitAnswer(recordId, questionIndex, answer) {
  return instance.post(`/student/exams/${recordId}/answer`, { question_index: questionIndex, answer })
}

export function submitAllAnswers(recordId) {
  return instance.post(`/student/exams/${recordId}/submit`)
}

export function getReport(recordId) {
  return instance.get(`/student/exams/${recordId}/report`)
}

export function getExamHistory() {
  return instance.get('/student/exams/history')
}

// Teacher exam APIs
export function createExamConfig(data) {
  return instance.post('/teacher/exams', data)
}

export function getTeacherExams(params = {}) {
  return instance.get('/teacher/exams', { params })
}

export function getExamResults(examId) {
  return instance.get(`/teacher/exams/${examId}/results`)
}

export function deleteExamConfig(examId) {
  return instance.delete(`/teacher/exams/${examId}`)
}

export function runCppCode(code, stdin = '') {
  return instance.post('/student/cpp-run', { code, stdin })
}
