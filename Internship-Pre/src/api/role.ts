import request from "@/utils/request";

export interface RoleRecord {
  id: number;
  role_name: string;
  role_key: string;
  role_sort: number;
  status: number;
  remark: string;
  create_time: string;
  update_time: string;
}

export interface RoleListParams {
  page?: number;
  pageSize?: number;
  role_name?: string;
  status?: number;
}

export interface ImportResult {
  success?: number;
  skipped?: number;
  errors?: string[];
  message?: string;
}

export function getRoleList(params: RoleListParams): Promise<{ records: RoleRecord[]; total: number }> {
  return request.get("/role/", { params });
}

export function createRole(data: Partial<RoleRecord>): Promise<RoleRecord> {
  return request.post("/role/", data);
}

export function updateRole(id: number, data: Partial<RoleRecord>): Promise<RoleRecord> {
  return request.put(`/role/${id}`, data);
}

export function deleteRole(id: number): Promise<void> {
  return request.delete(`/role/${id}`);
}

export function batchDeleteRoles(ids: number[]): Promise<void> {
  return request.delete("/role/batch", { data: { ids } });
}

export function getAllRoles(): Promise<RoleRecord[]> {
  return request.get("/role/all");
}

export function updateRoleSort(id: number, sortOrder: number): Promise<void> {
  return request.put(`/role/${id}/sort`, { sortOrder });
}

export function batchSortRoles(data: { id: number; sortOrder: number }[]): Promise<void> {
  return request.post("/role/batch-sort", data);
}

export function exportRoles(): Promise<Blob> {
  return request.get("/role/export", { responseType: "blob" });
}

export function downloadRoleTemplate(): Promise<Blob> {
  return request.get("/role/template", { responseType: "blob" });
}

export function importRoles(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/role/import", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function updateRoleStatus(id: number, status: number): Promise<void> {
  return request.put(`/role/${id}/status`, { status });
}

export function getRoleMenus(id: number): Promise<number[]> {
  return request.get(`/role/${id}/menus`);
}

export function assignRoleMenus(id: number, menu_ids: number[]): Promise<void> {
  return request.put(`/role/${id}/menus`, { menu_ids });
}

export function getRoleUsers(id: number): Promise<number[]> {
  return request.get(`/role/${id}/users`);
}

export function assignRoleUsers(id: number, user_ids: number[]): Promise<void> {
  return request.put(`/role/${id}/users`, { user_ids });
}
