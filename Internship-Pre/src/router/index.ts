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
  // RAG 知识库模块
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
  {
    path: "/",
    redirect: "/dashboard",
  },
  // 错误页面
  {
    path: "/403",
    name: "Forbidden",
    component: () => import("@/views/error/403.vue"),
    meta: { title: "无权限", layout: false },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("@/views/error/404.vue"),
    meta: { title: "页面不存在", layout: false },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: staticRoutes,
});

const whiteList = ["/login", "/403"];

let dynamicRoutesLoading: Promise<void> | null = null;

router.beforeEach(async (to) => {
  document.title = to.meta.title ? `${to.meta.title} - 管理系统` : "管理系统";
  const authStore = useAuthStore();
  if (to.path === "/login" && authStore.token) return "/dashboard";
  if (whiteList.includes(to.path)) return true;
  if (!authStore.token) return "/login";

  // 刷新后动态路由丢失 → 重新加载
  if (!authStore.dynamicRoutesLoaded) {
    if (!dynamicRoutesLoading) {
      dynamicRoutesLoading = authStore.generateDynamicRoutes().finally(() => {
        dynamicRoutesLoading = null;
      });
    }
    await dynamicRoutesLoading;
    // 路由加载完毕后，用实际路径重新导航
    return to.path === "/dashboard" ? true : to.path;
  }
});

export default router;
