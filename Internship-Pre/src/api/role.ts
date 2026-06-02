import request from "@/utils/request";

export function getRoleList(params: any) {
  return request.get("/role/list", { params });
}

export function getAllRoles() {
  return request.get("/role/all");
}

export function getRoleDetail(id: number) {
  return request.get(`/role/${id}`);
}

export function createRole(data: any) {
  return request.post("/role", data);
}

export function updateRole(id: number, data: any) {
  return request.put(`/role/${id}`, data);
}

export function deleteRole(id: number) {
  return request.delete(`/role/${id}`);
}

export function batchDeleteRoles(ids: number[]) {
  return request.delete("/role/batch", { data: { ids } });
}

export function updateRoleStatus(id: number, status: number) {
  return request.put(`/role/${id}/status`, { status });
}

export function getRoleMenus(id: number) {
  return request.get(`/role/${id}/menus`);
}

export function assignRoleMenus(id: number, menuIds: number[]) {
  return request.put(`/role/${id}/menus`, { menuIds });
}

export function getRoleUsers(id: number) {
  return request.get(`/role/${id}/users`);
}

export function assignRoleUsers(id: number, userIds: number[]) {
  return request.put(`/role/${id}/users`, { userIds });
}
