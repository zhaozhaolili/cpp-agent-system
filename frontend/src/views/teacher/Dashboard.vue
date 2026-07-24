<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <h2>教师仪表盘</h2>

        <!-- 统计卡片 -->
        <el-row :gutter="16" style="margin-bottom:20px;">
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">{{ data.student_count }}</div>
              <div class="stat-label">学生数</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">{{ data.material_count }}</div>
              <div class="stat-label">课件资料</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">{{ data.config_count }}</div>
              <div class="stat-label">考核配置</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">{{ data.total_submissions }}</div>
              <div class="stat-label">提交总数</div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 平均分 + 分数分布 -->
        <el-row :gutter="16" style="margin-bottom:20px;">
          <el-col :span="8">
            <el-card>
              <template #header><h3 style="margin:0;">平均成绩</h3></template>
              <div style="text-align:center;font-size:48px;font-weight:700;color:#409EFF;">{{ data.avg_score }}</div>
              <div style="text-align:center;color:#999;">分</div>
            </el-card>
          </el-col>
          <el-col :span="16">
            <el-card>
              <template #header><h3 style="margin:0;">分数分布</h3></template>
              <div v-for="(count, range) in data.score_distribution" :key="range" style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;">
                  <span>{{ range }}</span>
                  <span>{{ count }} 人</span>
                </div>
                <el-progress
                  :percentage="data.total_submissions ? Math.round(count / data.total_submissions * 100) : 0"
                  :color="distColor(range)"
                  :stroke-width="14"
                />
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 章节通过率 -->
        <el-card v-if="Object.keys(data.chapter_pass_rate || {}).length > 0" style="margin-bottom:20px;">
          <template #header><h3 style="margin:0;">章节通过率（≥60分）</h3></template>
          <div v-for="(info, title) in data.chapter_pass_rate" :key="title" style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;">
              <span>{{ title }}</span>
              <span>{{ info.passed }}/{{ info.total }} · {{ info.rate }}%</span>
            </div>
            <el-progress :percentage="info.rate" :color="info.rate >= 60 ? '#67C23A' : '#F56C6C'" :stroke-width="14" />
          </div>
        </el-card>

        <!-- 最近活动 -->
        <el-card>
          <template #header><h3 style="margin:0;">最近提交</h3></template>
          <el-table :data="data.recent_activity" stripe empty-text="暂无提交">
            <el-table-column prop="student_name" label="学生" width="120" />
            <el-table-column prop="chapter_title" label="章节" />
            <el-table-column prop="score" label="成绩" width="80">
              <template #default="{ row }">{{ row.score != null ? Math.round(row.score) : '-' }}</template>
            </el-table-column>
            <el-table-column prop="completed_at" label="时间" width="180">
              <template #default="{ row }">{{ formatDate(row.completed_at) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import { getTeacherDashboard } from '../../api/dashboard'
import { formatDate } from '../../utils/format'

const data = ref({
  student_count: 0, material_count: 0, config_count: 0,
  total_submissions: 0, avg_score: 0,
  score_distribution: {}, chapter_pass_rate: {}, recent_activity: []
})

onMounted(async () => {
  try {
    const res = await getTeacherDashboard()
    data.value = res.data
  } catch { /* ignore */ }
})

function distColor(range) {
  const map = { '0-39': '#F56C6C', '40-59': '#E6A23C', '60-79': '#409EFF', '80-100': '#67C23A' }
  return map[range] || '#909399'
}
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #409EFF; margin-bottom: 4px; }
.stat-label { font-size: 13px; color: #999; }
</style>
