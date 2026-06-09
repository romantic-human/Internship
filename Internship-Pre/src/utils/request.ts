import axios, { type AxiosResponse, type InternalAxiosRequestConfig } from "axios";
import { ElMessage, ElMessageBox } from "element-plus";
import { useAuthStore } from "@/store/auth";

function getToken(): string {
  return localStorage.getItem("access_token") || "";
}

function sanitizeValue(val: any): any {
  if (typeof val === "string") {
    return val.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }
  if (Array.isArray(val)) {
    return val.map(sanitizeValue);
  }
  if (val !== null && typeof val === "object") {
    const sanitized: Record<string, any> = {};
    for (const key of Object.keys(val)) {
      sanitized[key] = sanitizeValue(val[key]);
    }
    return sanitized;
  }
  return val;
}

function needsSanitize(url: string): boolean {
  const skipPaths = ["/user/refresh-token", "/user/login"];
  return !skipPaths.some((p) => url.includes(p));
}
function getRefreshToken(): string {
  return localStorage.getItem("refresh_token") || "";
}

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
});

let isRefreshing = false;
let pendingQueue: Array<{ resolve: (token: string) => void; reject: (err: any) => void }> = [];

function processQueue(err: any, token = "") {
  pendingQueue.forEach((p) => (err ? p.reject(err) : p.resolve(token)));
  pendingQueue = [];
}

async function handleTokenRefresh(error: any, refreshToken: string) {
  if (!isRefreshing) {
    isRefreshing = true;
    try {
      const res = await axios.post("/api/user/refresh-token/", { refresh: refreshToken });
      const newToken = res.data.data.access_token;
      const authStore = useAuthStore();
      authStore.setTokens(newToken, res.data.data.refresh_token);
      processQueue(null, newToken);
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return request(error.config);
    } catch (refreshErr) {
      processQueue(refreshErr);
      useAuthStore().logout();
      ElMessageBox.alert("登录已过期，请重新登录", "提示", {
        confirmButtonText: "确定",
        type: "warning",
      }).finally(() => {
        window.location.href = "/login";
      });
      return Promise.reject(refreshErr);
    } finally {
      isRefreshing = false;
    }
  }
  return new Promise((resolve, reject) => {
    pendingQueue.push({
      resolve: (token: string) => {
        error.config.headers.Authorization = `Bearer ${token}`;
        resolve(request(error.config));
      },
      reject,
    });
  });
}

request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

request.interceptors.response.use(
  (response: AxiosResponse) => {
    // blob 响应直接返回，不做 JSON 解析
    if (response.config.responseType === 'blob') {
      return response.data;
    }
    const res = response.data;
    if (res.code === 200 || res.code === 1000) {
      // XSS 防护：对用户输入内容做 HTML 转义
      if (needsSanitize(response.config.url || "")) {
        return sanitizeValue(res.data);
      }
      return res.data;
    }
    ElMessage.error(res.message || "请求失败");
    return Promise.reject(res);
  },
  async (error) => {
    if (!error.response) {
      ElMessage.error("网络错误，请检查后端服务");
      return Promise.reject(error);
    }
    const { status, data } = error.response;

    const refreshToken = useAuthStore().refreshToken;
    const needRefresh = (status === 401 && data?.code === "token_not_valid") || data?.code === 3001;
    if (needRefresh && refreshToken) {
      return handleTokenRefresh(error, refreshToken);
    }

    if (data?.code === 3002 || data?.code === 3000) {
      ElMessage.error("登录已失效，请重新登录");
      useAuthStore().logout();
      window.location.href = "/login";
      return Promise.reject(error);
    }

    if (data?.code === 3003) {
      ElMessage.error("无操作权限");
      // 跳转到 403 页面
      window.location.href = "/403";
      return Promise.reject(error);
    } else if (status !== 401) {
      ElMessage.error(data?.message || `请求错误 ${status}`);
    }
    return Promise.reject(error);
  },
);

export default request;
