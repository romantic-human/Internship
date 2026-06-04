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
          <el-dropdown trigger="click" @command="appStore.setTheme">
            <el-button link class="theme-btn">
              <el-icon size="16"><component :is="themeIcon" /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="light" :class="{ active: appStore.theme === 'light' }">
                  <el-icon><Sunny /></el-icon> 明亮
                </el-dropdown-item>
                <el-dropdown-item command="dark" :class="{ active: appStore.theme === 'dark' }">
                  <el-icon><Moon /></el-icon> 暗黑
                </el-dropdown-item>
                <el-dropdown-item command="blue" :class="{ active: appStore.theme === 'blue' }">
                  <el-icon><MagicStick /></el-icon> 蓝色
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
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
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";
import { computed, type Component } from "vue";
import { Fold, Expand, ArrowDown, User, SwitchButton, Sunny, Moon, MagicStick, House, Setting, Document, Tools, Key, OfficeBuilding, Menu as MenuIcon } from "@element-plus/icons-vue";
import { useAppStore, type ThemeName } from "@/store/app";
import { useAuthStore } from "@/store/auth";

const router = useRouter();
const route = useRoute();
const appStore = useAppStore();
const authStore = useAuthStore();
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed);

const themeIconMap: Record<ThemeName, Component> = { light: Sunny, dark: Moon, blue: MagicStick };
const themeIcon = computed(() => themeIconMap[appStore.theme]);

const iconMap: Record<string, Component> = { House, Setting, User, Document, Tools, Key, OfficeBuilding, Menu: MenuIcon };

const menuItems = [
  { path: "/dashboard", icon: "House", title: "首页" },
  {
    path: "/system", icon: "Setting", title: "系统管理",
    children: [
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
.layout-aside { background: var(--sidebar-bg); transition: width 0.28s; overflow: hidden; }
.logo { height: 56px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: 700; background: var(--sidebar-logo-bg); white-space: nowrap; overflow: hidden; }
.layout-menu { border-right: none; }
.layout-main { display: flex; flex-direction: column; }
.layout-header { display: flex; align-items: center; justify-content: space-between; height: 50px; background: var(--header-bg); border-bottom: 1px solid var(--header-border); padding: 0 16px; }
.header-right { display: flex; align-items: center; gap: 8px; }
.user-dropdown { display: flex; align-items: center; gap: 6px; cursor: pointer; }
.username { font-size: 14px; color: var(--text-regular); }
.theme-btn { color: var(--text-regular); }
:deep(.theme-btn:hover) { color: var(--text-primary); }
.layout-content { background: var(--main-bg); padding: 16px; overflow-y: auto; height: calc(100vh - 50px); }
:deep(.el-menu) { background: var(--sidebar-bg); }
:deep(.el-menu-item), :deep(.el-sub-menu__title) { color: var(--sidebar-text); }
:deep(.el-menu-item:hover), :deep(.el-sub-menu__title:hover) { background: var(--sidebar-hover-bg); }
:deep(.el-menu-item.is-active) { color: var(--sidebar-active-text); background: var(--sidebar-hover-bg); }
:deep(.el-dropdown-menu__item.active) { color: #409eff; font-weight: 600; }
</style>
