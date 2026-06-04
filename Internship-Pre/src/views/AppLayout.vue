<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside :width="collapsed ? '64px' : '220px'" class="app-aside">
      <div class="logo">
        <span v-if="!collapsed">组织架构管理</span>
        <span v-else>OA</span>
      </div>

      <el-menu
        :default-active="currentRoute"
        :collapse="collapsed"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu index="/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/user">用户管理</el-menu-item>
          <el-menu-item index="/system/role">角色管理</el-menu-item>
          <el-menu-item index="/system/menu">菜单管理</el-menu-item>
          <el-menu-item index="/system/permission">权限管理</el-menu-item>
          <el-menu-item index="/system/department">部门管理</el-menu-item>
          <el-menu-item index="/system/log">操作日志</el-menu-item>
          <el-menu-item index="/system/config">系统配置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 右侧区域 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="app-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="collapsed = !collapsed">
            <Fold v-if="!collapsed" /><Expand v-else />
          </el-icon>
        </div>
        <div class="header-right">
          <!-- 主题切换 -->
          <el-tooltip :content="isDark ? '切换亮色模式' : '切换暗色模式'" placement="bottom">
            <el-icon class="theme-btn" @click="handleToggleTheme">
              <Moon v-if="!isDark" />
              <Sunny v-else />
            </el-icon>
          </el-tooltip>

          <el-dropdown trigger="click">
            <span class="user-dropdown">
              <el-avatar :size="28">{{ authStore.userInfo?.nickname?.charAt(0) || "U" }}</el-avatar>
              <span>{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { HomeFilled, Setting, Fold, Expand, ArrowDown, Moon, Sunny } from "@element-plus/icons-vue";
import { useAuthStore } from "@/store/auth";
import { getTheme, toggleTheme } from "@/utils/theme";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const collapsed = ref(false);
const isDark = ref(getTheme() === "dark");

const currentRoute = computed(() => route.path);

function handleToggleTheme() {
  toggleTheme();
  isDark.value = getTheme() === "dark";
}

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
}

.app-aside {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.15);
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 16px;
  height: 50px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-btn {
  font-size: 18px;
  cursor: pointer;
  color: #909399;
  transition: color 0.3s, transform 0.3s;
}

.theme-btn:hover {
  color: #409EFF;
  transform: rotate(15deg);
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
}

.app-main {
  background: #f0f2f5;
  padding: 16px;
}
</style>