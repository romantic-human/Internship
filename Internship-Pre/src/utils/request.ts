import axios, { type AxiosResponse, type InternalAxiosRequestConfig } from "axios";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/store/auth";

function getToken(): string {
  return localStorage.getItem("access_token") || "";
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
    const res = response.data;
    if (res.code === 200 || res.code === 1000) {
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
    const authStore = useAuthStore();

    if (data?.code === 3002) {
      authStore.logout();
      window.location.href = "/login";
      return Promise.reject(error);
    }

    if (data?.code === 3001 && getRefreshToken()) {
      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const res = await axios.post("/api/user/refresh-token", { refresh: getRefreshToken() });
          const newToken = res.data.data.access_token;
          authStore.setTokens(newToken, res.data.data.refresh_token);
          processQueue(null, newToken);
          error.config.headers.Authorization = `Bearer ${newToken}`;
          return request(error.config);
        } catch (refreshErr) {
          processQueue(refreshErr);
          authStore.logout();
          window.location.href = "/login";
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

    switch (data?.code) {
      case 3000:
        ElMessage.error("登录已失效，请重新登录");
        authStore.logout();
        window.location.href = "/login";
        break;
      case 3003:
        ElMessage.error("无操作权限");
        break;
      default:
        ElMessage.error(data?.message || `请求错误 ${status}`);
    }
    return Promise.reject(error);
  },
);

export default request;