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
}): Promise<LoginResult> {
  return request.post("/user/register", data);
}

export function refreshTokenApi(data: { refresh: string }): Promise<{ access_token: string; refresh_token: string }> {
  return request.post("/user/refresh-token", data);
}

// ── 个人中心 ───────────────────────────────────────────────
export function getUserProfile(): Promise<{
  nickname: string; real_name: string; email: string; telephone: string;
  gender: number; avatar: string; department_id: number | null;
}> {
  return request.get("/user/profile");
}

export function updateUserProfile(data: Partial<{ nickname: string; real_name: string; email: string; telephone: string; gender: number }>): Promise<void> {
  return request.put("/user/profile", data);
}

export function updatePassword(data: {
  old_password: string;
  new_password: string;
}): Promise<void> {
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
  role_name?: string;
  role_ids: number[];
  last_login?: string | null;
  create_time: string;
}

export interface UserListParams {
  page?: number;
  pageSize?: number;
  username?: string;
  status?: number;
  department_id?: number;
  role_id?: number;
  start_date?: string;
  end_date?: string;
}

export interface ImportResult {
  success: number;
  skipped: number;
  errors: string[];
}

export function getUserList(params: UserListParams): Promise<{ records: UserRecord[]; total: number }> {
  return request.get("/user/", { params });
}

export function getUserDetail(id: number): Promise<UserRecord> {
  return request.get(`/user/${id}`);
}

export function createUser(data: Partial<UserRecord> & { password?: string }): Promise<UserRecord> {
  return request.post("/user/", data);
}

export function updateUser(id: number, data: Partial<UserRecord>): Promise<UserRecord> {
  return request.put(`/user/${id}`, data);
}

export function deleteUser(id: number): Promise<void> {
  return request.delete(`/user/${id}`);
}

export function batchDeleteUsers(ids: number[]): Promise<void> {
  return request.delete("/user/batch", { data: { ids } });
}

export function updateUserStatus(id: number, status: number): Promise<void> {
  return request.put(`/user/${id}/status`, { status });
}

export function resetPassword(data: { userId: number; password?: string }): Promise<void> {
  return request.put("/user/reset-password", data);
}

export function checkUnique(field: string, value: string, excludeId?: number): Promise<{ unique: boolean }> {
  return request.get("/user/check-unique", { params: { field, value, exclude_id: excludeId } });
}

// ── 导出 / 导入 ───────────────────────────────────────────────
export function downloadUserTemplate(): Promise<Blob> {
  return request.get("/user/template", { responseType: "blob" });
}

export function exportUsers(params?: UserListParams): Promise<Blob> {
  return request.get("/user/export", { params, responseType: "blob" });
}

export function importUsers(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/user/import", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
