<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <el-main>
        <h2>学习仪表盘</h2>

        <!-- 统计卡片 -->
        <el-row :gutter="16" style="margin-bottom:24px;">
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon" style="background:#eef2ff;color:#6366f1;"><el-icon :size="22"><Document /></el-icon></div>
              <div class="stat-body">
                <div class="stat-num">{{ data.completed_exams }}<span class="stat-total">/{{ data.total_chapters }}</span></div>
                <div class="stat-label">已完成章节</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon" style="background:#f0fdf4;color:#10b981;"><el-icon :size="22"><Trophy /></el-icon></div>
              <div class="stat-body">
                <div class="stat-num">{{ data.avg_score }}<span class="stat-total"> 分</span></div>
                <div class="stat-label">平均成绩</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon" style="background:#fff7ed;color:#f59e0b;"><el-icon :size="22"><Warning /></el-icon></div>
              <div class="stat-body">
                <div class="stat-num">{{ data.wrong_count }}</div>
                <div class="stat-label">错题数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon" style="background:#fef2f2;color:#ef4444;"><el-icon :size="22"><TrendCharts /></el-icon></div>
              <div class="stat-body">
                <div class="stat-num">{{ data.progress_percent }}%</div>
                <div class="stat-label">学习进度</div>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 能力维度 -->
        <el-card v-if="Object.keys(data.dimensions || {}).length > 0" style="margin-bottom:20px;">
          <template #header><h3 style="margin:0;">能力维度</h3></template>
          <el-row :gutter="24">
            <el-col :span="8" v-for="(val, key) in data.dimensions" :key="key">
              <div style="margin-bottom:8px;font-size:14px;">{{ key }}</div>
              <el-progress :percentage="Math.round(val)" :color="dimColor(val)" :stroke-width="14" />
            </el-col>
          </el-row>
        </el-card>

        <!-- 最近考核 -->
        <el-card>
          <template #header><h3 style="margin:0;">最近考核记录</h3></template>
          <el-table :data="data.recent_exams" stripe empty-text="暂无考核记录">
            <el-table-column prop="chapter_title" label="章节" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : 'warning'" size="small">
                  {{ row.status === 'completed' ? '已完成' : '进行中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="成绩" width="80">
              <template #default="{ row }">{{ row.score != null ? Math.round(row.score) : '-' }}</template>
            </el-table-column>
            <el-table-column prop="completed_at" label="完成时间" width="180">
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
import { getStudentDashboard } from '../../api/dashboard'
import { formatDate } from '../../utils/format'

const data = ref({
  total_chapters: 0, completed_exams: 0, progress_percent: 0,
  avg_score: 0, dimensions: {}, wrong_count: 0, recent_exams: []
})

onMounted(async () => {
  try {
    const res = await getStudentDashboard()
    data.value = res.data
  } catch { /* ignore */ }
})

function dimColor(val) {
  if (val >= 80) return '#67C23A'
  if (val >= 60) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style scoped>
.stat-card {
  display: flex; align-items: center; gap: 14px;
  background: #fff; border-radius: 12px; padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.stat-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-num { font-size: 22px; font-weight: 700; color: #1e293b; }
.stat-total { font-size: 14px; font-weight: 400; color: #94a3b8; }
.stat-label { font-size: 12px; color: #94a3b8; margin-top: 2px; }
</style>
