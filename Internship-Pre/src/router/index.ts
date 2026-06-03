import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/store/auth";

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
    meta: { title: "首页", layout: true },
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
    meta: { title: "部门管理(组长)" },
  },
  {
    path: "/system/menu",
    name: "Menu",
    component: () => import("@/views/system/menu/MenuTree.vue"),
    meta: { title: "菜单管理" },
  },
  {
    path: "/system/department",
    name: "DeptTree",
    component: () => import("@/views/system/department/DeptTree.vue"),
    meta: { title: "部门管理" },
  },
  {
    path: "/system/permission",
    name: "Permission",
    component: () => import("@/views/system/permission/PermissionList.vue"),
    meta: { title: "权限管理" },
  },
  {
    path: "/system/log",
    name: "Log",
    component: () => import("@/views/system/log/LogList.vue"),
    meta: { title: "操作日志" },
  },
  {
    path: "/system/config",
    name: "Config",
    component: () => import("@/views/system/config/ConfigList.vue"),
    meta: { title: "系统配置" },
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

const whiteList = ["/login"];

router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - 管理系统` : "管理系统";
  if (whiteList.includes(to.path)) return true;
  const authStore = useAuthStore();
  if (!authStore.token) return "/login";
});

export default router;
