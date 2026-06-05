<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面未找到</h2>
      <p class="error-desc">抱歉，您访问的页面不存在或已被移除。</p>
      <el-button type="primary" @click="$router.push('/dashboard')">返回首页</el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f0f2f5;
}
.not-found-content { text-align: center; }
.error-code { font-size: 120px; color: #409eff; margin: 0; line-height: 1; }
.error-title { font-size: 24px; color: #333; margin: 16px 0; }
.error-desc { color: #999; margin-bottom: 24px; }
</style>
