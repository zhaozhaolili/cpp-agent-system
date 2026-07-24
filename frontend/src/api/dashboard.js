import instance from './axios'

export function getStudentDashboard() {
  return instance.get('/dashboard/student')
}

export function getTeacherDashboard() {
  return instance.get('/dashboard/teacher')
}
