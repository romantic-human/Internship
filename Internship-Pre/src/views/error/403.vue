<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-icon">
        <svg viewBox="0 0 120 120" width="120" height="120">
          <circle cx="60" cy="60" r="56" fill="none" stroke="#f56c6c" stroke-width="3" opacity="0.3" />
          <circle cx="60" cy="60" r="44" fill="none" stroke="#f56c6c" stroke-width="2" opacity="0.2" />
          <path d="M40 45 L50 55 M50 45 L40 55" stroke="#f56c6c" stroke-width="3" stroke-linecap="round" />
          <path d="M70 45 L80 55 M80 45 L70 55" stroke="#f56c6c" stroke-width="3" stroke-linecap="round" />
          <path d="M42 78 Q60 68 78 78" fill="none" stroke="#f56c6c" stroke-width="3" stroke-linecap="round" />
        </svg>
      </div>
      <h1 class="error-code">403</h1>
      <h2 class="error-title">抱歉，您没有权限访问此页面</h2>
      <p class="error-desc">
        当前账号权限不足，如需访问请联系管理员分配权限。
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
  color: #f56c6c;
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

.dark .error-code { color: #f89898; }
</style>
