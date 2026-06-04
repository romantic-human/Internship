import request from "@/utils/request";

// ── 认证接口 ────────────────────────────────────────────────
export function login(data: { username: string; password: string }) {
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
export function getUserProfile() {
  return request.get("/user/profile");
}

export function updateUserProfile(data: any) {
  return request.put("/user/profile", data);
}

export function updatePassword(data: {
  oldPassword: string;
  newPassword: string;
}) {
  return request.put("/user/update-password", data);
}

export function uploadAvatar(file: File) {
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
  email: string;
  telephone: string;
  status: number;
  create_time: string;
}

export function getUserList(params: any): Promise<{ records: UserRecord[]; total: number }> {
  return request.get("/user/", { params });
}

export function createUser(data: any) {
  return request.post("/user/", data);
}

export function updateUser(id: number, data: any) {
  return request.put(`/user/${id}`, data);
}

export function deleteUser(id: number) {
  return request.delete(`/user/${id}`);
}

export function updateUserStatus(id: number, status: number) {
  return request.put(`/user/${id}/status`, { status });
}

export function resetPassword(data: { userId: number; password?: string }) {
  return request.put("/user/reset-password", data);
}