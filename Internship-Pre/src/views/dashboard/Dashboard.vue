<template>
  <div class="dashboard">
    <div class="header-bar">
      <h1>组织架构管理系统</h1>
      <div class="user-area">
        <el-dropdown trigger="click">
          <span class="user-dropdown">
            <el-avatar :size="32">
              {{ authStore.userInfo?.nickname?.charAt(0) || "U" }}
            </el-avatar>
            <span class="username">{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goProfile">
                <el-icon><User /></el-icon>个人中心
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="welcome-section">
      <h2>欢迎回来，{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</h2>
      <p class="welcome-desc">请从左侧菜单选择功能模块开始使用</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { ArrowDown, User, SwitchButton } from "@element-plus/icons-vue";
import { useAuthStore } from "@/store/auth";

const router = useRouter();
const authStore = useAuthStore();

function goProfile() {
  router.push("/profile");
}

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f7fa;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-bar h1 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-area {
  cursor: pointer;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-size: 14px;
  color: #606266;
}

.welcome-section {
  text-align: center;
  padding: 80px 24px;
}

.welcome-section h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 12px;
}

.welcome-desc {
  font-size: 14px;
  color: #909399;
}
</style>