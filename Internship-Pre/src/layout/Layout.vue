<template>
  <el-container class="layout-container">
    <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="layout-aside">
      <div class="logo" :style="{ width: sidebarCollapsed ? '64px' : '220px' }">
        <span v-if="!sidebarCollapsed">企业智能分析平台</span>
        <span v-else>智</span>
      </div>
      <div class="menu-scroll">
      <div v-if="!sidebarCollapsed" class="breadcrumb-bar">
        <el-icon><House /></el-icon>
        <span>{{ route.meta?.title || '' }}</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="sidebarCollapsed"
        :router="true"
        :collapse-transition="false"
        unique-opened
        :key="menuKey"
        class="layout-menu"
      >
          <template v-for="item in sidebarMenus" :key="item.id">
            <!-- 单页菜单 -->
            <el-menu-item v-if="item.menu_type === 1" :index="item.path!">
              <el-icon><component :is="resolveIcon(item.icon)" /></el-icon>
              <template #title>{{ item.menu_name }}</template>
            </el-menu-item>

            <!-- 目录菜单 -->
            <el-sub-menu v-else-if="item.children && item.children.length > 0" :index="String(item.id)">
              <template #title>
                <el-icon><component :is="resolveIcon(item.icon)" /></el-icon>
                <span>{{ item.menu_name }}</span>
              </template>
              <el-menu-item
                v-for="child in flattenMenuChildren(item.children)"
                :key="child.id"
                :index="child.path!"
              >
                <el-icon><component :is="resolveIcon(child.icon)" /></el-icon>
                <template #title>{{ child.menu_name }}</template>
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </div>
      <div v-if="!sidebarCollapsed" class="collapse-all-btn" @click="collapseAllMenus">
        <el-icon><Fold /></el-icon><span>折叠菜单</span>
      </div>
    </el-aside>
    <el-container class="layout-main">
      <el-header class="layout-header">
        <el-button link @click="appStore.toggleSidebar">
          <el-icon size="18"><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </el-button>
        <div class="header-right">
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
      <TabsNav />
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
import { computed, markRaw, ref, type Component } from "vue";
import {
  Fold, Expand, ArrowDown, User, SwitchButton,
  House, Setting, Document, Tools, Key, OfficeBuilding,
  Menu as MenuIcon, Moon, Sunny, UserFilled,
  Monitor, Collection, Notebook, ChatDotRound, FolderOpened, Connection, Reading, TrendCharts, Avatar, Bell,
} from "@element-plus/icons-vue";
import { useAppStore } from "@/store/app";
import { useAuthStore } from "@/store/auth";
import type { MenuItem } from "@/api/menu";
import TabsNav from "@/components/TabsNav.vue";
const router = useRouter();
const route = useRoute();
const appStore = useAppStore();
const authStore = useAuthStore();
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed);
const isDark = computed(() => appStore.theme === "dark");
const menuKey = ref(0);
function collapseAllMenus() {
  menuKey.value++;
}

function handleToggleTheme() {
  appStore.setTheme(appStore.theme === "dark" ? "light" : "dark");
}

const iconMap: Record<string, Component> = {
  House: markRaw(House), Setting: markRaw(Setting), User: markRaw(User),
  UserFilled: markRaw(UserFilled), Document: markRaw(Document),
  Tools: markRaw(Tools), Key: markRaw(Key),
  Office: markRaw(OfficeBuilding), OfficeBuilding: markRaw(OfficeBuilding),
  Menu: markRaw(MenuIcon), Moon: markRaw(Moon), Sunny: markRaw(Sunny), Monitor: markRaw(Monitor),
  Collection: markRaw(Collection), Notebook: markRaw(Notebook),
  ChatDotRound: markRaw(ChatDotRound), FolderOpened: markRaw(FolderOpened),
  Connection: markRaw(Connection), Reading: markRaw(Reading), TrendCharts: markRaw(TrendCharts),
  Avatar: markRaw(Avatar), Bell: markRaw(Bell),
};

function resolveIcon(iconName: string) {
  return iconMap[iconName] || MenuIcon;
}

/** 从菜单树构建侧边栏数据结构 — 只展示目录(0)和菜单(1)，过滤隐藏/禁用的 */
const sidebarMenus = computed(() => {
  const tree = authStore.menuTree;
  if (!tree || tree.length === 0) {
    // fallback：静态菜单（动态路由加载前显示）
    return [
      { id: 0, menu_type: 1, menu_name: "首页", path: "/dashboard", icon: "House" },
    ] as MenuItem[];
  }
  return tree;
});

/** 扁平的子菜单（去除不可见的按钮类型） */
function flattenMenuChildren(children: MenuItem[]): MenuItem[] {
  return children.filter(
    (c) => c.visible === 1 && c.status === 1 && c.menu_type === 1 && c.path
  );
}

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style scoped>
.layout-container { height: 100vh; }

/* ── 侧边栏 ──────────────────────────────────────── */
.layout-aside {
  background: var(--sidebar-bg);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 10;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  background: rgba(0, 0, 0, 0.2);
  white-space: nowrap;
  overflow: hidden;
  letter-spacing: 2px;
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.layout-menu {
  border-right: none;
}

.breadcrumb-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.breadcrumb-bar .el-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.menu-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;
}
.menu-scroll::-webkit-scrollbar { width: 4px; }
.menu-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
}
.menu-scroll::-webkit-scrollbar-track { background: transparent; }

/* ── 菜单项样式 ──────────────────────────────────────── */
:deep(.el-menu) {
  background: transparent;
  border-right: none;
}
:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: var(--sidebar-text);
  border-radius: 8px;
  margin: 2px 8px;
  height: 44px;
  line-height: 44px;
  transition: all 0.2s ease;
}
:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: var(--sidebar-hover);
  color: #fff;
}
:deep(.el-menu-item.is-active) {
  color: #fff;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.4) 0%, rgba(139, 92, 246, 0.3) 100%);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
}
:deep(.el-sub-menu .el-menu-item) {
  padding-left: 52px !important;
  height: 40px;
  line-height: 40px;
  font-size: 13px;
}

/* 暗色模式下的菜单样式 */
:global(.dark) :deep(.el-menu-item:hover),
:global(.dark) :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.05);
  color: #c7d2fe;
}
:global(.dark) :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.2) 100%);
  color: #fff;
}

.collapse-all-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  color: var(--sidebar-text);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.collapse-all-btn:hover {
  background: var(--sidebar-hover);
  color: #fff;
}

/* 暗色模式下的折叠按钮 */
:global(.dark) .collapse-all-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* ── 主内容区 ──────────────────────────────────────── */
.layout-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height, 56px);
  background: var(--header-bg, rgba(255, 255, 255, 0.8));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 5;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  padding: 6px;
  border-radius: 8px;
}
.theme-btn:hover {
  color: var(--primary-color);
  transform: rotate(15deg);
  background: var(--primary-light);
}

/* 暗色模式下的主题按钮 */
:global(.dark) .theme-btn:hover {
  background: rgba(99, 102, 241, 0.08);
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px 4px 4px;
  border-radius: 24px;
  transition: all 0.2s ease;
}
.user-dropdown:hover {
  background: var(--bg-color-secondary);
}

/* 暗色模式下的用户下拉 */
:global(.dark) .user-dropdown:hover {
  background: rgba(255, 255, 255, 0.05);
}

.username {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.layout-content {
  background: var(--bg-color);
  padding: 20px 24px;
  overflow-y: auto;
  height: calc(100vh - var(--header-height, 56px));
  min-width: 0;
}

/* ── 暗色模式 ──────────────────────────────────────── */
:global(.dark) .layout-header {
  background: rgba(15, 23, 42, 0.85);
  border-bottom-color: var(--border-color);
}
:global(.dark) .layout-content {
  background: var(--bg-color);
}
</style>
