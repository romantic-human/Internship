<template>
  <el-container class="layout-container">
    <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="layout-aside">
      <div class="logo" :style="{ width: sidebarCollapsed ? '64px' : '220px' }">
        <span v-if="!sidebarCollapsed">管理系统</span>
        <span v-else>M</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="sidebarCollapsed"
        :router="true"
        :collapse-transition="false"
        class="layout-menu"
      >
        <template v-for="item in menuItems" :key="item.path">
          <el-menu-item v-if="!item.children" :index="item.path">
            <el-icon><component :is="iconMap[item.icon]" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
          <el-sub-menu v-else :index="item.path">
            <template #title>
              <el-icon><component :is="iconMap[item.icon]" /></el-icon>
              <span>{{ item.title }}</span>
            </template>
            <el-menu-item v-for="child in item.children" :key="child.path" :index="child.path">
              <el-icon><component :is="iconMap[child.icon]" /></el-icon>
              <template #title>{{ child.title }}</template>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-aside>
    <el-container class="layout-main">
      <el-header class="layout-header">
        <el-button link @click="appStore.toggleSidebar">
          <el-icon size="18"><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </el-button>
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
              <span class="username">{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";
import { computed, ref } from "vue";
import { Fold, Expand, ArrowDown, User, SwitchButton, House, Setting, Document, Tools, Key, OfficeBuilding, Menu as MenuIcon, Moon, Sunny } from "@element-plus/icons-vue";
import { useAppStore } from "@/store/app";
import { useAuthStore } from "@/store/auth";
import { getTheme, toggleTheme } from "@/utils/theme";

const router = useRouter();
const route = useRoute();
const appStore = useAppStore();
const authStore = useAuthStore();
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed);

const isDark = ref(getTheme() === "dark");

function handleToggleTheme() {
  toggleTheme();
  isDark.value = getTheme() === "dark";
}

const iconMap: Record<string, any> = { House, Setting, User, Document: Document as any, Tools: Tools as any, Key: Key as any, OfficeBuilding, Menu: MenuIcon as any };

const menuItems = [
  { path: "/dashboard", icon: "House", title: "首页" },
  {
    path: "/system", icon: "Setting", title: "系统管理",
    children: [
      { path: "/system/user", icon: "User", title: "用户管理" },
      { path: "/system/role", icon: "Setting", title: "角色管理" },
      { path: "/system/menu", icon: "Menu", title: "菜单管理" },
      { path: "/system/department", icon: "OfficeBuilding", title: "部门管理" },
      { path: "/system/permission", icon: "Key", title: "权限管理" },
      { path: "/system/log", icon: "Document", title: "操作日志" },
      { path: "/system/config", icon: "Tools", title: "系统配置" },
    ],
  },
  { path: "/profile", icon: "User", title: "个人中心" },
];

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.layout-aside { background: #304156; transition: width 0.28s; overflow: hidden; }
.logo { height: 56px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: 700; background: #2b3a4a; white-space: nowrap; overflow: hidden; }
.layout-menu { border-right: none; }
.layout-main { display: flex; flex-direction: column; }
.layout-header { display: flex; align-items: center; justify-content: space-between; height: 50px; background: var(--el-bg-color, #fff); border-bottom: 1px solid var(--el-border-color-light, #e4e7ed); padding: 0 16px; }
.header-right { display: flex; align-items: center; gap: 12px; }

.theme-btn { font-size: 18px; cursor: pointer; color: #909399; transition: color 0.3s, transform 0.3s; }
.theme-btn:hover { color: #409EFF; transform: rotate(15deg); }
.user-dropdown { display: flex; align-items: center; gap: 6px; cursor: pointer; }
.username { font-size: 14px; color: var(--el-text-color-regular, #606266); }
.layout-content { background: var(--el-bg-color-page, #f5f7fa); padding: 16px; overflow-y: auto; height: calc(100vh - 50px); }
:deep(.el-menu) { background: #304156; }
:deep(.el-menu-item), :deep(.el-sub-menu__title) { color: #bfcbd9; }
:deep(.el-menu-item:hover), :deep(.el-sub-menu__title:hover) { background: #263445; }
:deep(.el-menu-item.is-active) { color: #409eff; background: #263445; }
</style>