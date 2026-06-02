import request from "@/utils/request";

// ── 认证接口 ────────────────────────────────────────────────
export function login(data: { username: string; password: string }) {
  return request.post("/user/login", data);
}

export function refreshTokenApi(data: { refresh: string }) {
  return request.post("/user/refresh-token", data);
}

// ── 用户管理 ───────────────────────────────────────────────
export function getUserList(params: any) {
  return request.get("/user/list", { params });
}

export function getUserDetail(id: number) {
  return request.get(`/user/${id}`);
}

export function createUser(data: any) {
  return request.post("/user", data);
}

export function updateUser(id: number, data: any) {
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

export function resetPassword(data: { userId: number }) {
  return request.put("/user/reset-password", data);
}

export function updatePassword(data: { oldPassword: string; newPassword: string }) {
  return request.put("/user/update-password", data);
}

export function getUserProfile() {
  return request.get("/user/profile");
}

export function updateUserProfile(data: any) {
  return request.put("/user/profile", data);
}