import request from "@/utils/request";

export interface LoginResult {
  access_token: string;
  refresh_token: string;
  user: {
    id: number;
    username: string;
    nickname: string;
    avatar?: string;
    permissions?: string[];
    roles?: string[];
  };
}

// ── 认证接口 ────────────────────────────────────────────────
export function login(data: { username: string; password: string }): Promise<LoginResult> {
  return request.post("/user/login", data);
}

export function register(data: {
  username: string;
  password: string;
  nickname?: string;
}) {
  return request.post("/user/register", data);
}

export function refreshTokenApi(data: { refresh: string }) {
  return request.post("/user/refresh-token", data);
}

// ── 个人中心 ───────────────────────────────────────────────
export function getUserProfile(): Promise<{
  nickname: string; real_name: string; email: string; telephone: string;
  gender: number; avatar: string; department_id: number | null;
}> {
  return request.get("/user/profile");
}

export function updateUserProfile(data: Record<string, any>) {
  return request.put("/user/profile", data);
}

export function updatePassword(data: {
  old_password: string;
  new_password: string;
}) {
  return request.put("/user/update-password", data);
}

export function uploadAvatar(file: File): Promise<{ url: string }> {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/user/avatar", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

// ── 用户管理 ───────────────────────────────────────────────
export interface UserRecord {
  id: number;
  username: string;
  nickname: string;
  real_name: string;
  email: string;
  telephone: string;
  gender: number;
  status: number;
  department_id: number | null;
  department_name?: string;
  create_time: string;
}

export function getUserList(params: Record<string, any>): Promise<{ records: UserRecord[]; total: number }> {
  return request.get("/user/", { params });
}

export function createUser(data: Partial<UserRecord> & { password?: string }) {
  return request.post("/user/", data);
}

export function updateUser(id: number, data: Partial<UserRecord>) {
  return request.put(`/user/${id}`, data);
}

export function deleteUser(id: number) {
  return request.delete(`/user/${id}`);
}

export function batchDeleteUsers(ids: number[]) {
  return request.delete("/user/batch", { data: { ids } });
}

export function updateUserStatus(id: number, status: number) {
  return request.put(`/user/${id}/status`, { status });
}

export function resetPassword(data: { userId: number; password?: string }) {
  return request.put("/user/reset-password", data);
}

// ── 导出 / 导入 ───────────────────────────────────────────────
export function exportUsers() {
  return request.get("/user/export", { responseType: "blob" });
}

export function importUsers(file: File): Promise<{ success: number; skipped: number; errors: string[] }> {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/user/import", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

// ── 密码重置请求 ───────────────────────────────────────────
export interface ResetRequestRecord {
  id: number;
  username: string;
  status: "pending" | "approved";
  created_at: string;
  handled_at: string | null;
  handler: number | null;
}

export function createResetRequest(username: string) {
  return request.post("/user/reset-request", { username });
}

export function getResetRequests(params?: Record<string, any>): Promise<ResetRequestRecord[]> {
  return request.get("/user/reset-requests", { params });
}

export function approveReset(data: { request_id: number; password?: string }): Promise<{ new_password: string }> {
  return request.put("/user/approve-reset", data);
}
