import { defineStore } from "pinia";
import { ref } from "vue";

export type ThemeName = "light" | "dark";

export const useAppStore = defineStore("app", () => {
  const sidebarCollapsed = ref(false);
  const theme = ref<ThemeName>((localStorage.getItem("theme") as ThemeName) || "light");

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

  return { sidebarCollapsed, toggleSidebar, theme, setTheme };
});