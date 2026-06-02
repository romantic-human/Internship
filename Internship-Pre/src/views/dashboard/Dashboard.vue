<template>
  <div class="dashboard">
    <h1>欢迎使用组织架构管理系统</h1>
    <p>当前用户：{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</p>
    <el-button type="danger" @click="handleLogout">退出登录</el-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "@/store/auth";

const router = useRouter();
const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style scoped>
.dashboard {
  padding: 40px;
  text-align: center;
}
</style>