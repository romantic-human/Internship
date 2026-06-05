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

export function getRoleList(params: Record<string, any>): Promise<{ records: RoleRecord[]; total: number }> {
  return request.get("/role/", { params });
}

export function createRole(data: Partial<RoleRecord>) {
  return request.post("/role/", data);
}

export function updateRole(id: number, data: Partial<RoleRecord>) {
  return request.put(`/role/${id}`, data);
}

export function deleteRole(id: number) {
  return request.delete(`/role/${id}`);
}

export function batchDeleteRoles(ids: number[]) {
  return request.delete("/role/batch", { data: { ids } });
}

export function getAllRoles(): Promise<RoleRecord[]> {
  return request.get("/role/all");
}

export function updateRoleSort(id: number, sortOrder: number) {
  return request.put(`/role/${id}/sort`, { sortOrder });
}

export function batchSortRoles(data: { id: number; sortOrder: number }[]) {
  return request.post("/role/batch-sort", data);
}

export function exportRoles() {
  return request.get("/role/export", { responseType: "blob" });
}

export function updateRoleStatus(id: number, status: number) {
  return request.put(`/role/${id}/status`, { status });
}

export function getRoleMenus(id: number): Promise<number[]> {
  return request.get(`/role/${id}/menus`);
}

export function assignRoleMenus(id: number, menu_ids: number[]) {
  return request.put(`/role/${id}/menus`, { menu_ids });
}

export function getRoleUsers(id: number): Promise<number[]> {
  return request.get(`/role/${id}/users`);
}

export function assignRoleUsers(id: number, user_ids: number[]) {
  return request.put(`/role/${id}/users`, { user_ids });
}
