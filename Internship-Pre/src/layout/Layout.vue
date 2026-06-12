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
import { computed, markRaw, type Component } from "vue";
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
