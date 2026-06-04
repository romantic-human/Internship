import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import "element-plus/theme-chalk/dark/css-vars.css";
import "./styles/index.css";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import App from "./App.vue";
import router from "./router";
import { setupPermissionDirective } from "./directives/permission";

// 初始化主题（在 app 挂载前）
if (localStorage.getItem("theme") === "dark") {
  document.documentElement.classList.add("dark");
}

const app = createApp(App);

// Element Plus
app.use(ElementPlus, { locale: zhCn });

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 状态管理 & 路由
app.use(createPinia());
app.use(router);

// 权限指令
setupPermissionDirective(app);

app.mount("#app");