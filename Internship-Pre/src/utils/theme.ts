/** 主题切换工具 */
const THEME_KEY = "theme";

export type Theme = "light" | "dark";

export function getTheme(): Theme {
  return (localStorage.getItem(THEME_KEY) as Theme) || "light";
}

export function setTheme(theme: Theme) {
  localStorage.setItem(THEME_KEY, theme);
  applyTheme(theme);
}

export function toggleTheme(): Theme {
  const next = getTheme() === "light" ? "dark" : "light";
  setTheme(next);
  return next;
}

export function applyTheme(theme: Theme) {
  if (theme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

/** 初始化主题（在 app 挂载前调用） */
export function initTheme() {
  const theme = getTheme();
  applyTheme(theme);
  // 监听系统主题变化
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (!localStorage.getItem(THEME_KEY)) {
      applyTheme(e.matches ? "dark" : "light");
    }
  });
}