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
        <template v-for="item in sidebarMenus" :key="item.id">
          <!-- 单页菜单 -->
          <el-tooltip
            v-if="item.menu_type === 1"
            :content="sidebarCollapsed ? item.menu_name : ''"
            placement="right"
            :disabled="!sidebarCollapsed"
          >
            <el-menu-item :index="item.path!">
              <el-icon><component :is="resolveIcon(item.icon)" /></el-icon>
              <template #title>{{ item.menu_name }}</template>
            </el-menu-item>
          </el-tooltip>

          <!-- 目录菜单 -->
          <el-sub-menu v-else-if="item.children && item.children.length > 0" :index="String(item.id)">
            <template #title>
              <el-icon><component :is="resolveIcon(item.icon)" /></el-icon>
              <span>{{ item.menu_name }}</span>
            </template>
            <el-tooltip
              v-for="child in flattenMenuChildren(item.children)"
              :key="child.id"
              :content="sidebarCollapsed ? child.menu_name : ''"
              placement="right"
              :disabled="!sidebarCollapsed"
            >
              <el-menu-item :index="child.path!">
                <el-icon><component :is="resolveIcon(child.icon)" /></el-icon>
                <template #title>{{ child.menu_name }}</template>
              </el-menu-item>
            </el-tooltip>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-aside>
    <el-container class="layout-main">
      <!-- 顶部 Loading 条 -->
      <div class="route-loading-bar" :class="{ active: appStore.routeLoading }" />
      <el-header class="layout-header">
        <div class="header-left">
          <el-button link @click="appStore.toggleSidebar">
            <el-icon size="18"><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
          </el-button>
          <!-- 面包屑 -->
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">
              <el-icon size="14"><House /></el-icon>
            </el-breadcrumb-item>
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path ? { path: item.path } : undefined"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
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
      <!-- Tab 页签 -->
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
import { computed, markRaw, watch, type Component } from "vue";
import {
  Fold, Expand, ArrowDown, User, SwitchButton,
  House, Setting, Document, Tools, Key, OfficeBuilding,
  Menu as MenuIcon, Moon, Sunny, UserFilled,
  Monitor,
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

function handleToggleTheme() {
  appStore.setTheme(appStore.theme === "dark" ? "light" : "dark");
}

const iconMap: Record<string, Component> = {
  House: markRaw(House), Setting: markRaw(Setting), User: markRaw(User),
  UserFilled: markRaw(UserFilled), Document: markRaw(Document),
  Tools: markRaw(Tools), Key: markRaw(Key),
  Office: markRaw(OfficeBuilding), OfficeBuilding: markRaw(OfficeBuilding),
  Monitor: markRaw(Monitor), Menu: markRaw(MenuIcon), Moon: markRaw(Moon), Sunny: markRaw(Sunny),
};

function resolveIcon(iconName: string) {
  return iconMap[iconName] || MenuIcon;
}

// ── 面包屑 ────────────────────────────────────────────
interface BreadcrumbItem {
  title: string;
  path?: string;
}

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const path = route.path;
  if (path === "/dashboard") return [];

  const menuTree = authStore.menuTree;
  const trail = findMenuTrail(menuTree, path);
  if (trail.length > 0) return trail;

  // fallback: 用 route.meta.title
  const title = (route.meta?.title as string) || "";
  return title ? [{ title, path }] : [];
});

function findMenuTrail(menus: MenuItem[], targetPath: string, trail: BreadcrumbItem[] = []): BreadcrumbItem[] {
  for (const menu of menus) {
    const current = { title: menu.menu_name, path: menu.menu_type === 1 ? menu.path : undefined };
    const newTrail = [...trail, current];

    if (menu.path === targetPath && menu.menu_type === 1) {
      return newTrail;
    }
    if (menu.children && menu.children.length > 0) {
      const result = findMenuTrail(menu.children, targetPath, newTrail);
      if (result.length > 0) return result;
    }
  }
  return [];
}

// ── 全局 Loading ────────────────────────────────────────
router.beforeEach(() => {
  appStore.routeLoading = true;
});
router.afterEach(() => {
  setTimeout(() => { appStore.routeLoading = false; }, 200);
});

// ── 侧边栏 ─────────────────────────────────────────────
const sidebarMenus = computed(() => {
  const tree = authStore.menuTree;
  if (!tree || tree.length === 0) {
    return [
      { id: 0, menu_type: 1, menu_name: "首页", path: "/dashboard", icon: "House" },
    ] as MenuItem[];
  }
  return tree;
});

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
.layout-aside { background: #304156; transition: width 0.28s; overflow: hidden; }
.logo { height: 56px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: 700; background: #2b3a4a; white-space: nowrap; overflow: hidden; }
.layout-menu { border-right: none; }
.layout-main { display: flex; flex-direction: column; position: relative; }

/* 顶部 Loading 条 */
.route-loading-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  z-index: 100;
  pointer-events: none;
}
.route-loading-bar::after {
  content: '';
  display: block;
  height: 100%;
  width: 0;
  background: var(--el-color-primary);
  transition: width 0.3s ease;
}
.route-loading-bar.active::after {
  width: 80%;
  transition: width 2s ease;
}

/* Header */
.layout-header { display: flex; align-items: center; justify-content: space-between; height: 50px; background: var(--el-bg-color, #fff); border-bottom: 1px solid var(--el-border-color-light, #e4e7ed); padding: 0 16px; }
.header-left { display: flex; align-items: center; gap: 8px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.breadcrumb { margin-left: 4px; }
:deep(.el-breadcrumb__inner a),
:deep(.el-breadcrumb__inner.is-link) { font-weight: normal; }

/* Theme */
.theme-btn { font-size: 18px; cursor: pointer; color: #909399; transition: color 0.3s, transform 0.3s; }
.theme-btn:hover { color: #409EFF; transform: rotate(15deg); }
.user-dropdown { display: flex; align-items: center; gap: 6px; cursor: pointer; }
.username { font-size: 14px; color: var(--el-text-color-regular, #606266); }
.layout-content { background: var(--el-bg-color-page, #f5f7fa); padding: 16px; overflow-y: auto; height: calc(100vh - 50px - 34px); }

/* Sidebar */
:deep(.el-menu) { background: #304156; }
:deep(.el-menu-item), :deep(.el-sub-menu__title) { color: #bfcbd9; }
:deep(.el-menu-item:hover), :deep(.el-sub-menu__title:hover) { background: #263445; }
:deep(.el-menu-item.is-active) { color: #409eff; background: #263445; }

/* 过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active { transition: all 0.25s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateX(12px); }
.fade-slide-leave-to { opacity: 0; transform: translateX(-12px); }

/* ── 暗色模式 ─────────────────────── */
.dark .layout-aside { background: #1a1b23; }
.dark .logo { background: #14151c; }
.dark :deep(.el-menu) { background: #1a1b23; }
.dark :deep(.el-menu-item),
.dark :deep(.el-sub-menu__title) { color: #a0a2a8; }
.dark :deep(.el-menu-item:hover),
.dark :deep(.el-sub-menu__title:hover) { background: #22232d; }
.dark :deep(.el-menu-item.is-active) { color: #409eff; background: #22232d; }
.dark .layout-header { background: #1e1f28; border-bottom-color: #2a2b36; }
.dark .layout-content { background: #14151c; }
.dark .username { color: #a0a2a8; }

/* ── 响应式 ─────────────────────── */
@media (max-width: 768px) {
  .layout-aside { position: fixed; left: 0; top: 0; bottom: 0; z-index: 1000; }
  .layout-main { margin-left: 0; }
  .username { display: none; }
}
</style>
