import { defineStore } from "pinia";
import { ref, watch } from "vue";

export type ThemeName = "light" | "dark" | "blue";

export const useAppStore = defineStore("app", () => {
  const sidebarCollapsed = ref(false);
  const theme = ref<ThemeName>((localStorage.getItem("theme") as ThemeName) || "light");

  watch(theme, (val) => {
    localStorage.setItem("theme", val);
    document.documentElement.setAttribute("data-theme", val);
  }, { immediate: true });

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  }

  function setTheme(t: ThemeName) {
    theme.value = t;
  }

  return { sidebarCollapsed, toggleSidebar, theme, setTheme };
});