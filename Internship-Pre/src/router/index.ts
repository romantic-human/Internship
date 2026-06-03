import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

// ── 静态路由（无需权限）──────────────────────────────────────
const staticRoutes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/login/Login.vue"),
    meta: { title: "登录" },
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
    path: "/department",
    name: "Department",
    component: () => import("@/views/system/department/DepartmentList.vue"),
    meta: { title: "部门管理" },
  },
  {
    path: "/",
    redirect: "/dashboard",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: staticRoutes,
});

export default router;