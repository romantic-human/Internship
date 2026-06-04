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
  {
    path: "/",
    redirect: "/dashboard",
  },
  // 捕获所有未匹配路由
  {
    path: "/:pathMatch(.*)*",
    redirect: "/dashboard",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: staticRoutes,
});

const whiteList = ["/login"];

let dynamicRoutesLoading: Promise<void> | null = null;

router.beforeEach(async (to) => {
  document.title = to.meta.title ? `${to.meta.title} - 管理系统` : "管理系统";

  if (whiteList.includes(to.path)) return true;

  const authStore = useAuthStore();
  if (!authStore.token) return "/login";
  if (to.path === "/login") return "/dashboard";

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
