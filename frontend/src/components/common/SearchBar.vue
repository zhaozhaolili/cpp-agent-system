<template>
  <div class="search-bar">
    <el-input
      v-model="keyword"
      placeholder="搜索对话、资料、错题..."
      :prefix-icon="Search"
      size="default"
      class="search-input"
      @keyup.enter="handleSearch"
      clearable
    >
      <template #append>
        <el-button :icon="Search" @click="handleSearch" />
      </template>
    </el-input>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const keyword = ref('')

function handleSearch() {
  const q = keyword.value.trim()
  if (q) {
    router.push({ path: '/search', query: { q } })
  }
}
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
}
.search-input {
  width: 320px;
}
.search-input :deep(.el-input__wrapper) {
  border-radius: 20px;
  background: #f1f5f9;
  border: none;
  box-shadow: none;
  transition: background .2s;
}
.search-input :deep(.el-input__wrapper:hover) {
  background: #e2e8f0;
}
.search-input :deep(.el-input__wrapper.is-focus) {
  background: #fff;
  box-shadow: 0 0 0 1px #6366f1;
}
.search-input :deep(.el-input-group__append) {
  border-radius: 0 20px 20px 0;
  background: transparent;
  border: none;
}
</style>
