<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-icon">
        <svg viewBox="0 0 120 120" width="120" height="120">
          <circle cx="60" cy="60" r="56" fill="none" stroke="#e6a23c" stroke-width="3" opacity="0.3" />
          <circle cx="60" cy="60" r="44" fill="none" stroke="#e6a23c" stroke-width="2" opacity="0.2" />
          <circle cx="45" cy="50" r="4" fill="#e6a23c" />
          <circle cx="75" cy="50" r="4" fill="#e6a23c" />
          <path d="M45 75 Q60 65 75 75" fill="none" stroke="#e6a23c" stroke-width="3" stroke-linecap="round" />
          <text x="60" y="95" text-anchor="middle" fill="#e6a23c" font-size="10" opacity="0.6">?</text>
        </svg>
      </div>
      <h1 class="error-code">404</h1>
      <h2 class="error-title">抱歉，您访问的页面不存在</h2>
      <p class="error-desc">
        页面可能已被删除、移动，或者您输入的地址有误。
      </p>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <el-icon><Back /></el-icon>
          返回上一页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { House, Back } from "@element-plus/icons-vue";

const router = useRouter();

function goHome() {
  router.push("/dashboard");
}

function goBack() {
  router.back();
}
</script>

<style scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  background: var(--el-bg-color-page, #f5f7fa);
}

.error-content {
  text-align: center;
  padding: 40px;
}

.error-icon {
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.error-code {
  font-size: 72px;
  font-weight: 800;
  color: #e6a23c;
  margin: 0;
  line-height: 1;
  letter-spacing: 4px;
}

.error-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary, #303133);
  margin: 16px 0 8px;
}

.error-desc {
  font-size: 14px;
  color: var(--el-text-color-secondary, #909399);
  margin: 0 0 32px;
  max-width: 360px;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.dark .error-code { color: #eebe77; }
</style>
