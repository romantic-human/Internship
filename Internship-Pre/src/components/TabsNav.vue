<template>
  <div class="tabs-nav">
    <div class="tabs-wrapper" ref="tabsWrapperRef">
      <div
        v-for="tab in appStore.visitedTabs"
        :key="tab.path"
        :class="['tab-item', { active: appStore.activeTab === tab.path }]"
        @click="handleClick(tab)"
        @contextmenu.prevent="handleContextMenu($event, tab)"
      >
        <span class="tab-title">{{ tab.title }}</span>
        <el-icon
          v-if="!tab.affix"
          class="tab-close"
          @click.stop="handleClose(tab)"
        >
          <Close />
        </el-icon>
      </div>
      <el-tooltip content="关闭所有标签" placement="bottom">
        <el-icon class="close-all-tabs" @click="handleCloseAll"><Close /></el-icon>
      </el-tooltip>
    </div>

    <!-- 右键菜单 -->
    <Teleport to="body">
      <div
        v-if="contextMenuVisible"
        class="tab-context-menu"
        :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }"
      >
        <div class="context-item" @click="handleCloseOther">关闭其他</div>
        <div class="context-item" @click="handleCloseAll">关闭所有</div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Close } from "@element-plus/icons-vue";
import { useAppStore, type TabItem } from "@/store/app";

const router = useRouter();
const route = useRoute();
const appStore = useAppStore();
const tabsWrapperRef = ref<HTMLElement>();

// 右键菜单
const contextMenuVisible = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const contextTab = ref<TabItem | null>(null);

function handleClick(tab: TabItem) {
  if (tab.path !== route.path) {
    router.push(tab.path);
  }
}

function handleClose(tab: TabItem) {
  const nextPath = appStore.removeTab(tab.path);
  if (nextPath) {
    router.push(nextPath);
  }
}

function handleContextMenu(e: MouseEvent, tab: TabItem) {
  if (tab.affix) return;
  contextTab.value = tab;
  contextMenuX.value = e.clientX;
  contextMenuY.value = e.clientY;
  contextMenuVisible.value = true;
}

function handleCloseOther() {
  if (contextTab.value) {
    appStore.closeOtherTabs(contextTab.value.path);
    if (contextTab.value.path !== route.path) {
      router.push(contextTab.value.path);
    }
  }
  contextMenuVisible.value = false;
}

function handleCloseAll() {
  const path = appStore.closeAllTabs();
  router.push(path);
  contextMenuVisible.value = false;
}

function closeContextMenu() {
  contextMenuVisible.value = false;
}

onMounted(() => {
  document.addEventListener("click", closeContextMenu);
});

onUnmounted(() => {
  document.removeEventListener("click", closeContextMenu);
});

// 监听路由变化，自动添加 tab
watch(
  () => route.path,
  (path) => {
    const title = (route.meta?.title as string) || "";
    const name = route.name as string | undefined;
    // 跳过登录、403、404 等页面，以及没有标题的页面
    if (["Login", "Forbidden", "NotFound"].includes(name || "")) return;
    if (!title) return;
    appStore.addTab({ path, title, name });
    // 滚动到激活的 tab
    scrollToActiveTab();
  },
  { immediate: true }
);

function scrollToActiveTab() {
  setTimeout(() => {
    const wrapper = tabsWrapperRef.value;
    if (!wrapper) return;
    const activeEl = wrapper.querySelector(".tab-item.active") as HTMLElement;
    if (activeEl) {
      activeEl.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }
  }, 100);
}
</script>

<style scoped>
.tabs-nav {
  display: flex;
  align-items: center;
  height: 34px;
  background: var(--el-bg-color, #fff);
  border-bottom: 1px solid var(--el-border-color-light, #e4e7ed);
  padding: 0 8px;
  overflow: hidden;
}

.tabs-wrapper {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  flex: 1;
}

.tabs-wrapper::-webkit-scrollbar {
  display: none;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 12px;
  color: var(--el-text-color-regular, #606266);
  background: var(--el-fill-color-light, #f5f7fa);
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  user-select: none;
  flex-shrink: 0;
}

.tab-item:hover {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.tab-item.active {
  color: #fff;
  background: var(--el-color-primary);
}

.tab-close {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  font-size: 10px;
  transition: all 0.2s;
}

.tab-close:hover {
  background: rgba(0, 0, 0, 0.15);
}

.tab-item.active .tab-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.close-all-tabs {
  font-size: 14px;
  cursor: pointer;
  color: var(--el-text-color-secondary, #909399);
  flex-shrink: 0;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}
.close-all-tabs:hover {
  color: var(--el-color-primary, #409eff);
  background: var(--el-color-primary-light-9);
}

.tab-context-menu {
  position: fixed;
  z-index: 9999;
  background: var(--el-bg-color, #fff);
  border: 1px solid var(--el-border-color-light, #e4e7ed);
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 4px 0;
  min-width: 100px;
}

.context-item {
  padding: 6px 16px;
  font-size: 13px;
  color: var(--el-text-color-regular, #606266);
  cursor: pointer;
  transition: background 0.2s;
}

.context-item:hover {
  background: var(--el-fill-color-light, #f5f7fa);
  color: var(--el-color-primary);
}

/* 暗色模式 */
.dark .tabs-nav {
  background: #1e1f28;
  border-bottom-color: #2a2b36;
}

.dark .tab-item {
  color: #a0a2a8;
  background: #2a2b36;
}

.dark .tab-item:hover {
  color: #409eff;
  background: rgba(64, 158, 255, 0.1);
}

.dark .tab-item.active {
  color: #fff;
  background: #409eff;
}

.dark .tab-context-menu {
  background: #2a2b36;
  border-color: #3a3b46;
}

.dark .context-item {
  color: #a0a2a8;
}

.dark .context-item:hover {
  background: #333440;
  color: #409eff;
}
</style>
