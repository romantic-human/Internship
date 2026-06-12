import { defineStore } from "pinia";
import { ref, watch } from "vue";

export type ThemeName = "light" | "dark";

export interface TabItem {
  path: string;
  title: string;
  name?: string;
  affix?: boolean; // 固定标签（如首页）
}

export const useAppStore = defineStore("app", () => {
  const sidebarCollapsed = ref(false);
  const theme = ref<ThemeName>((localStorage.getItem("theme") as ThemeName) || "light");
  const routeLoading = ref(false);
  const visitedTabs = ref<TabItem[]>([
    { path: "/dashboard", title: "首页", name: "Dashboard", affix: true },
  ]);
  const activeTab = ref("/dashboard");

  function applyTheme(t: ThemeName) {
    localStorage.setItem("theme", t);
    if (t === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  }

  function setTheme(t: ThemeName) {
    theme.value = t;
    applyTheme(t);
  }

  /** 添加/激活一个标签 */
  function addTab(tab: TabItem) {
    activeTab.value = tab.path;
    const existing = visitedTabs.value.find((t) => t.path === tab.path);
    if (!existing) {
      visitedTabs.value.push(tab);
    }
  }

  /** 关闭标签 */
  function removeTab(path: string): string | undefined {
    const idx = visitedTabs.value.findIndex((t) => t.path === path);
    if (idx === -1) return undefined;
    const tab = visitedTabs.value[idx];
    if (tab.affix) return undefined; // 固定标签不可关闭
    visitedTabs.value.splice(idx, 1);
    // 如果关闭的是当前激活标签，切换到相邻标签
    if (activeTab.value === path) {
      const next = visitedTabs.value[idx] || visitedTabs.value[idx - 1];
      return next?.path;
    }
    return undefined;
  }

  /** 关闭其他标签 */
  function closeOtherTabs(path: string) {
    visitedTabs.value = visitedTabs.value.filter((t) => t.affix || t.path === path);
    activeTab.value = path;
  }

  /** 关闭所有标签（保留固定标签） */
  function closeAllTabs(): string {
    visitedTabs.value = visitedTabs.value.filter((t) => t.affix);
    const first = visitedTabs.value[0];
    activeTab.value = first?.path || "/dashboard";
    return activeTab.value;
  }

  return {
    sidebarCollapsed, toggleSidebar,
    theme, setTheme,
    routeLoading,
    visitedTabs, activeTab,
    addTab, removeTab, closeOtherTabs, closeAllTabs,
  };
});