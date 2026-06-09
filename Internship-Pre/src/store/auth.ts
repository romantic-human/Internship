import { defineStore } from "pinia";
import { ref } from "vue";
import { login as loginApi } from "@/api/user";
import { getMenuTree, type MenuItem } from "@/api/menu";
import type { RouteRecordRaw } from "vue-router";

export interface UserInfo {
  id?: number;
  username?: string;
  nickname?: string;
  avatar?: string;
  roles?: string[];
  permissions?: string[];
}

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string>(localStorage.getItem("access_token") || "");
  const refreshToken = ref<string>(localStorage.getItem("refresh_token") || "");
  const userInfo = ref<UserInfo | null>(null);
  const permissions = ref<string[]>(JSON.parse(localStorage.getItem("permissions") || "[]"));
  const roles = ref<string[]>(JSON.parse(localStorage.getItem("roles") || "[]"));
  const dynamicRoutesLoaded = ref(false);
  const menuTree = ref<MenuItem[]>([]);

  function setAuthData(res: {
    access_token: string;
    refresh_token: string;
    user: UserInfo & { permissions?: string[]; roles?: string[] };
  }) {
    token.value = res.access_token;
    refreshToken.value = res.refresh_token;
    userInfo.value = res.user;
    permissions.value = res.user.permissions || [];
    roles.value = res.user.roles || [];
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    localStorage.setItem("permissions", JSON.stringify(permissions.value));
    localStorage.setItem("roles", JSON.stringify(roles.value));
  }

  async function login(username: string, password: string) {
    const res = await loginApi({ username, password });
    setAuthData(res);
    await generateDynamicRoutes();
  }

  /** 登出 */
  function logout() {
    token.value = "";
    refreshToken.value = "";
    userInfo.value = null;
    permissions.value = [];
    roles.value = [];
    menuTree.value = [];
    dynamicRoutesLoaded.value = false;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("permissions");
    localStorage.removeItem("roles");
  }

  /** 动态生成路由（根据菜单树） */
  async function generateDynamicRoutes() {
    if (dynamicRoutesLoaded.value) return;
    try {
      const menus = await getMenuTree();
      menuTree.value = menus;

      // 清除旧的动态路由，重新注册
      const { default: router } = await import("@/router");
      const routes = buildRoutesFromMenu(menus);

      // 移除已存在的同名路由后重新添加
      routes.forEach((r) => {
        if (r.name) {
          const existing = router.getRoutes().find((rr) => rr.name === r.name);
          if (existing) router.removeRoute(r.name as string);
        }
        router.addRoute(r);
      });
    } catch {
      menuTree.value = [];
    } finally {
      dynamicRoutesLoaded.value = true;
    }
  }

  /** 检查权限 */
  function hasPermission(perm: string): boolean {
    if (!perm) return false;
    return permissions.value.includes(perm) || permissions.value.includes("*:*:*");
  }

  /** 设置 Token（用于 refresh 后更新） */
  function setTokens(access: string, refresh: string) {
    token.value = access;
    refreshToken.value = refresh;
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  }

  return {
    token,
    refreshToken,
    userInfo,
    permissions,
    roles,
    menuTree,
    dynamicRoutesLoaded,
    login,
    logout,
    setTokens,
    generateDynamicRoutes,
    hasPermission,
  };
});

/**
 * 组件路径 → Vue 组件动态导入映射
 * 菜单表中的 component 字段如 "system/user/UserList"
 */
const componentMap: Record<string, () => Promise<any>> = {
  "system/user/UserList": () => import("@/views/system/user/UserList.vue"),
  "system/role/RoleList": () => import("@/views/system/role/RoleList.vue"),
  "system/menu/MenuTree": () => import("@/views/system/menu/MenuTree.vue"),
  "system/department/DeptTree": () => import("@/views/system/department/DeptTree.vue"),
  "system/permission/PermissionList": () => import("@/views/system/permission/PermissionList.vue"),
  "system/log/LogList": () => import("@/views/system/log/LogList.vue"),
  "system/config/ConfigList": () => import("@/views/system/config/ConfigPanel.vue"),
  "system/config/ConfigPanel": () => import("@/views/system/config/ConfigPanel.vue"),
  "system/config/ConfigAdvanced": () => import("@/views/system/config/ConfigList.vue"),
};

function getComponent(componentPath: string) {
  if (componentMap[componentPath]) return componentMap[componentPath];
  // fallback: 尝试动态拼接路径
  return () => import(`@/views/${componentPath}.vue`);
}

/**
 * 递归将菜单树转换为 vue-router 路由
 * - menu_type=0(目录) → 递归处理 children
 * - menu_type=1(菜单) → 生成 RouteRecordRaw
 * - menu_type=2(按钮) → 跳过
 */
function buildRoutesFromMenu(menus: MenuItem[]): RouteRecordRaw[] {
  const routes: RouteRecordRaw[] = [];

  for (const menu of menus) {
    // 只处理可见且启用的菜单
    if (menu.visible !== 1 || menu.status !== 1) continue;

    if (menu.menu_type === 1 && menu.path) {
      // 菜单 → 注册路由
      routes.push({
        path: menu.path,
        name: menu.menu_name,
        component: getComponent(menu.component),
        meta: { title: menu.menu_name, icon: menu.icon },
      });
    }

    // 目录 → 递归
    if (menu.children && menu.children.length > 0) {
      routes.push(...buildRoutesFromMenu(menu.children));
    }
  }

  return routes;
}
