<template>
  <div class="dashboard">
    <h2>欢迎回来，{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</h2>
    <p>请从左侧菜单选择功能模块开始使用</p>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/store/auth";
const authStore = useAuthStore();
</script>

<style scoped>
.dashboard {
  text-align: center;
  padding: 60px 24px;
}
h2 { font-size: 24px; color: #303133; margin-bottom: 8px; }
p { font-size: 14px; color: #909399; }
</style>