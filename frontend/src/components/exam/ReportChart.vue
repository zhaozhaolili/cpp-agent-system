<template>
  <div class="report-chart">
    <h3>评价维度</h3>
    <div class="dimensions">
      <div v-for="(val, key) in dimensions" :key="key" class="dim-item">
        <div class="dim-label">{{ key }}</div>
        <el-progress :percentage="Math.round(val)" :color="getColor(val)" :stroke-width="16" />
      </div>
    </div>
    <div class="score-section">
      <h2>总分: {{ Math.round(score) }} / 100</h2>
    </div>
    <div v-if="reviewPoints.length" class="review-section">
      <h4>复习建议</h4>
      <ul>
        <li v-for="(pt, i) in reviewPoints" :key="i">{{ pt }}</li>
      </ul>
    </div>
    <div class="comment-section">
      <h4>综合评价</h4>
      <p>{{ comment }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  dimensions: { type: Object, default: () => ({}) },
  score: { type: Number, default: 0 },
  reviewPoints: { type: Array, default: () => [] },
  comment: { type: String, default: '' },
})

function getColor(val) {
  if (val >= 80) return '#67C23A'
  if (val >= 60) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style scoped>
.report-chart {
  padding: 20px;
}
.dimensions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin: 16px 0;
}
.dim-label {
  font-size: 14px;
  margin-bottom: 4px;
  font-weight: 500;
}
.score-section {
  text-align: center;
  margin: 24px 0;
  color: #409EFF;
}
.review-section ul {
  padding-left: 20px;
}
.review-section li {
  margin: 6px 0;
  color: #E6A23C;
}
.comment-section p {
  color: #666;
  line-height: 1.8;
}
</style>
