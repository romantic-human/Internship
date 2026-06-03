import request from "@/utils/request";

export interface PermissionItem {
  id: number;
  permission_name: string;
  permission_key: string;
  sort_order: number;
  status: number;
  create_time: string;
}

export function getPermissionList(params: Record<string, any>): Promise<{ records: PermissionItem[]; total: number }> {
  return request.get("/permission/", { params });
}

export function getPermissionDetail(id: number): Promise<PermissionItem> {
  return request.get(`/permission/${id}`);
}

export function createPermission(data: Partial<PermissionItem>) {
  return request.post("/permission/", data);
}

export function updatePermission(id: number, data: Partial<PermissionItem>) {
  return request.put(`/permission/${id}`, data);
}

export function deletePermission(id: number) {
  return request.delete(`/permission/${id}`);
}

export function getPermissionMenus(id: number): Promise<number[]> {
  return request.get(`/permission/${id}/menus`);
}

export function bindPermissionMenus(id: number, menuIds: number[]) {
  return request.put(`/permission/${id}/menus`, { menuIds });
}

export function updatePermissionSort(id: number, sortOrder: number) {
  return request.put(`/permission/${id}/sort`, { sortOrder });
}

export function batchSortPermission(data: { id: number; sortOrder: number }[]) {
  return request.post("/permission/batch-sort", data);
}
