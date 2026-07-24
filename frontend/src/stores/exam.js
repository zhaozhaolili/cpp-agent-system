import { defineStore } from 'pinia'
import { ref } from 'vue'
import { startExam, submitAnswer, submitAllAnswers } from '../api/exam'

export const useExamStore = defineStore('exam', () => {
  const recordId = ref(null)
  const questions = ref([])
  const answers = ref({})
  const currentIndex = ref(0)
  const isSubmitting = ref(false)
  const report = ref(null)

  async function startExamAction(configId) {
    const res = await startExam(configId)
    recordId.value = res.data.record_id
    questions.value = res.data.questions
    answers.value = {}
    currentIndex.value = 0
    report.value = null
    return res.data
  }

  async function answerQuestion(index, answer) {
    answers.value[index] = answer
    if (recordId.value) {
      await submitAnswer(recordId.value, index, answer)
    }
  }

  async function submitAll() {
    if (!recordId.value) return
    isSubmitting.value = true
    try {
      const answerList = questions.value.map((_, i) => answers.value[i] || '(未作答)')
      const res = await submitAllAnswers(recordId.value)
      report.value = res.data
      return res.data
    } finally {
      isSubmitting.value = false
    }
  }

  function nextQuestion() {
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
    }
  }

  function prevQuestion() {
    if (currentIndex.value > 0) {
      currentIndex.value--
    }
  }

  function goToQuestion(index) {
    if (index >= 0 && index < questions.value.length) {
      currentIndex.value = index
    }
  }

  function reset() {
    recordId.value = null
    questions.value = []
    answers.value = {}
    currentIndex.value = 0
    isSubmitting.value = false
    report.value = null
  }

  return {
    recordId, questions, answers, currentIndex, isSubmitting, report,
    startExamAction, answerQuestion, submitAll,
    nextQuestion, prevQuestion, goToQuestion, reset,
  }
})
