import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/store/auth";

/** 静态路由 — 不依赖菜单树的页面 */
const staticRoutes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/login/Login.vue"),
    meta: { title: "登录", layout: false },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("@/views/dashboard/Dashboard.vue"),
    meta: { title: "首页" },
  },
  {
    path: "/profile",
    name: "Profile",
    component: () => import("@/views/system/profile/Profile.vue"),
    meta: { title: "个人中心" },
  },
  // RAG 静态路由（同时支持动态路由，双重保障）
  {
    path: "/rag/kb-list",
    name: "KBList",
    component: () => import("@/views/rag/KBList.vue"),
    meta: { title: "知识库管理" },
  },
  {
    path: "/rag/kb-detail",
    name: "KBDetail",
    component: () => import("@/views/rag/KBDetail.vue"),
    meta: { title: "知识库详情" },
  },
  {
    path: "/rag/chat",
    name: "ChatView",
    component: () => import("@/views/rag/ChatView.vue"),
    meta: { title: "AI 问答" },
  },
  // NL2SQL 静态路由
  {
    path: "/nl2sql/query",
    name: "NL2SQLQuery",
    component: () => import("@/views/nl2sql/QueryView.vue"),
    meta: { title: "自然语言查询" },
  },
  {
    path: "/nl2sql/history",
    name: "NL2SQLHistory",
    component: () => import("@/views/nl2sql/HistoryList.vue"),
    meta: { title: "查询历史" },
  },
  {
    path: "/nl2sql/datasource",
    name: "NL2SQLDataSource",
    component: () => import("@/views/nl2sql/DataSourceList.vue"),
    meta: { title: "数据源管理" },
  },
  {
    path: "/",
    redirect: "/dashboard",
  },
  // 错误页面（必须在 catch-all 之前注册）
  {
    path: "/403",
    name: "Forbidden",
    component: () => import("@/views/error/403.vue"),
    meta: { title: "无权限", layout: false },
  },
  {
    path: "/404",
    name: "NotFound",
    component: () => import("@/views/error/404.vue"),
    meta: { title: "页面不存在", layout: false },
  },
  // 捕获所有未匹配路由 → 重定向到 404
  {
    path: "/:pathMatch(.*)*",
    redirect: "/404",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: staticRoutes,
});

const whiteList = ["/login", "/403", "/404"];

let dynamicRoutesLoading: Promise<void> | null = null;

let regenerationAttempted = false;

router.beforeEach(async (to) => {
  document.title = to.meta.title ? `${to.meta.title} - 管理系统` : "管理系统";
  const authStore = useAuthStore();
  if (to.path === "/login" && authStore.token) return "/dashboard";
  if (whiteList.includes(to.path)) return true;
  if (!authStore.token) return "/login";

  // HMR/刷新后动态路由可能丢失 → 强制重新生成（最多一次）
  const routeExists = router.getRoutes().some(r => r.path === to.path) || to.matched.length > 0;
  if (!authStore.dynamicRoutesLoaded || (!routeExists && !regenerationAttempted)) {
    regenerationAttempted = true;
    if (!dynamicRoutesLoading) {
      dynamicRoutesLoading = authStore.generateDynamicRoutes(true).finally(() => {
        dynamicRoutesLoading = null;
      });
    }
    await dynamicRoutesLoading;
    if (!router.getRoutes().some(r => r.path === to.path)) {
      return "/dashboard";
    }
    return to.path;
  }
  return true;
});

export default router;
