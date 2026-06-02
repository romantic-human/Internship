import axios, { type AxiosResponse, type InternalAxiosRequestConfig } from "axios";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/store/auth";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
});

// ── 请求拦截器 ──────────────────────────────────────────────
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ── 响应拦截器 ──────────────────────────────────────────────
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data;
    // 业务成功
    if (res.code === 200 || res.code === 1000) {
      return res.data;
    }
    // 业务错误
    ElMessage.error(res.message || "请求失败");
    return Promise.reject(res);
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      switch (data?.code) {
        case 3000: // Token 缺失
        case 3002: // Token 无效
          ElMessage.error("登录已失效，请重新登录");
          useAuthStore().logout();
          window.location.href = "/login";
          break;
        case 3001: // Token 过期 → 自动刷新
          // TODO: 调用 refresh-token 接口
          ElMessage.error("Token 已过期");
          break;
        case 3003: // 无权限
          ElMessage.error("无操作权限");
          break;
        default:
          ElMessage.error(data?.message || `请求错误 ${status}`);
      }
    } else {
      ElMessage.error("网络错误，请检查后端服务");
    }
    return Promise.reject(error);
  },
);

export default request;
