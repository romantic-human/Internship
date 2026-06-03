import { defineStore } from "pinia";
import { ref } from "vue";
import { login as loginApi, register as registerApi } from "@/api/user";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string>(localStorage.getItem("access_token") || "");
  const refreshToken = ref<string>(localStorage.getItem("refresh_token") || "");
  const userInfo = ref<any>(null);
  const permissions = ref<string[]>([]);
  const roles = ref<string[]>([]);
  const dynamicRoutesLoaded = ref(false);

  /** 注册 */
  async function register(username: string, password: string, nickname?: string) {
    const res = await registerApi({ username, password, nickname });
    token.value = res.access_token;
    refreshToken.value = res.refresh_token;
    userInfo.value = res.user;
    permissions.value = res.user.permissions || [];
    roles.value = res.user.roles || [];
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    await generateDynamicRoutes();
  }

  /** 登录 */
  async function login(username: string, password: string) {
    const res = await loginApi({ username, password });
    token.value = res.access_token;
    refreshToken.value = res.refresh_token;
    userInfo.value = res.user;
    permissions.value = res.user.permissions || [];
    roles.value = res.user.roles || [];
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    await generateDynamicRoutes();
  }

  /** 登出 */
  function logout() {
    token.value = "";
    refreshToken.value = "";
    userInfo.value = null;
    permissions.value = [];
    roles.value = [];
    dynamicRoutesLoaded.value = false;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  /** 动态生成路由（根据菜单树） */
  async function generateDynamicRoutes() {
    // TODO: 调用 /api/menu/tree 获取菜单树，动态生成路由
    dynamicRoutesLoaded.value = true;
  }

  /** 检查权限 */
  function hasPermission(perm: string): boolean {
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
    dynamicRoutesLoaded,
    register,
    login,
    logout,
    setTokens,
    generateDynamicRoutes,
    hasPermission,
  };
});