<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <div v-if="!examStore.questions.length" style="text-align:center;padding-top:100px;">
          <el-button type="primary" :loading="loadingStart" size="large" @click="startExamAction">开始考核</el-button>
        </div>

        <template v-else-if="!submitted">
          <div style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
            <h3>第 {{ examStore.currentIndex + 1 }} / {{ examStore.questions.length }} 题</h3>
            <div style="display:flex;align-items:center;gap:12px;">
              <span v-if="timeLeft > 0" :style="{color: timeLeft < 60 ? '#F56C6C' : '#E6A23C', fontWeight:'bold'}">
                剩余 {{ Math.floor(timeLeft / 60) }}:{{ String(timeLeft % 60).padStart(2, '0') }}
              </span>
              <el-button type="success" @click="handleSubmit">交卷</el-button>
            </div>
          </div>

          <QuestionCard
            v-if="currentQuestion"
            :key="examStore.currentIndex"
            :question="currentQuestion"
            :model-value="examStore.answers[examStore.currentIndex] || ''"
            @change="handleAnswer"
          />

          <div style="display:flex;justify-content:center;gap:12px;margin-top:16px;">
            <el-button :disabled="examStore.currentIndex === 0" @click="examStore.prevQuestion">上一题</el-button>
            <el-button :disabled="examStore.currentIndex === examStore.questions.length - 1" @click="examStore.nextQuestion">下一题</el-button>
          </div>
        </template>

        <template v-else>
          <ReportChart
            v-if="examStore.report"
            :dimensions="examStore.report.dimensions"
            :score="examStore.report.score"
            :review-points="examStore.report.review_points"
            :comment="examStore.report.overall_comment"
          />
          <div style="text-align:center;margin-top:20px;">
            <el-button type="primary" @click="$router.push('/student/exams')">返回考核列表</el-button>
          </div>
        </template>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import QuestionCard from '../../components/exam/QuestionCard.vue'
import ReportChart from '../../components/exam/ReportChart.vue'
import { useExamStore } from '../../stores/exam'
import { ElMessage } from 'element-plus'

const route = useRoute()
const examStore = useExamStore()
const loadingStart = ref(false)
const submitted = ref(false)
const timeLimit = ref(0)  // minutes
const timeLeft = ref(0)   // seconds
let timerInterval = null

examStore.reset()

const configId = computed(() => parseInt(route.params.id))
const currentQuestion = computed(() => examStore.questions[examStore.currentIndex] || null)

async function startExamAction() {
  loadingStart.value = true
  try {
    const data = await examStore.startExamAction(configId.value)
    timeLimit.value = data.time_limit_minutes || 0
    timeLeft.value = timeLimit.value * 60
    if (timeLeft.value > 0) {
      timerInterval = setInterval(() => {
        timeLeft.value--
        if (timeLeft.value <= 0) {
          clearInterval(timerInterval)
          handleSubmit()
        }
      }, 1000)
    }
  } catch (e) {
    ElMessage.error('开始考核失败')
  } finally {
    loadingStart.value = false
  }
}

function handleAnswer({ index, answer }) {
  examStore.answerQuestion(index, answer)
}

async function handleSubmit() {
  try {
    await examStore.submitAll()
    submitted.value = true
    ElMessage.success('交卷成功')
  } catch (e) {
    ElMessage.error('提交失败')
  }
}
</script>
