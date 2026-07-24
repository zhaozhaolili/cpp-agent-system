<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <div v-if="loading" style="text-align:center;padding-top:100px;">
          <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        </div>
        <template v-else-if="report">
          <ReportChart
            :dimensions="report.dimensions"
            :score="report.score"
            :review-points="report.review_points"
            :comment="report.overall_comment"
          />
          <div style="text-align:center;margin-top:20px;">
            <a :href="'/api/v1/student/exams/' + recordId + '/export'" target="_blank">
              <el-button type="primary">导出 PDF</el-button>
            </a>
            <el-button @click="$router.push('/student/exams')">返回考核列表</el-button>
          </div>
        </template>
        <el-empty v-else description="报告不存在" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import ReportChart from '../../components/exam/ReportChart.vue'
import { getReport } from '../../api/exam'

const route = useRoute()
const recordId = route.params.id
const report = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getReport(parseInt(route.params.id))
    report.value = res.data
  } catch { /* ignore */ }
  finally { loading.value = false }
})
</script>
