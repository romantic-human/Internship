import request from "@/utils/request";

export interface MenuItem {
  id: number;
  parent_id: number | null;
  menu_name: string;
  menu_type: number;
  path: string;
  component: string;
  icon: string;
  permission: string;
  sort_order: number;
  visible: number;
  is_frame: number;
  status: number;
  create_time: string;
  update_time: string;
  children?: MenuItem[];
}

export interface MenuListParams {
  menu_name?: string;
}

export function getMenuTree(params?: MenuListParams): Promise<MenuItem[]> {
  return request.get("/menu/tree", { params });
}

export function getMenuOptions(): Promise<MenuItem[]> {
  return request.get("/menu/options");
}

export function getMenuDetail(id: number): Promise<MenuItem> {
  return request.get(`/menu/${id}`);
}

export function createMenu(data: Partial<MenuItem>): Promise<MenuItem> {
  return request.post("/menu/", data);
}

export function updateMenu(id: number, data: Partial<MenuItem>): Promise<MenuItem> {
  return request.put(`/menu/${id}`, data);
}

export function deleteMenu(id: number): Promise<void> {
  return request.delete(`/menu/${id}`);
}

export function updateMenuStatus(id: number, status: number): Promise<void> {
  return request.put(`/menu/${id}/status`, { status });
}

export function updateMenuSort(id: number, sortOrder: number): Promise<void> {
  return request.put(`/menu/${id}/sort`, { sortOrder });
}

export function batchSortMenu(data: { id: number; sortOrder: number }[]): Promise<void> {
  return request.post("/menu/batch-sort", data);
}

export function batchDeleteMenus(ids: number[]): Promise<void> {
  return request.delete("/menu/batch", { data: { ids } });
}

export function exportMenus(): Promise<Blob> {
  return request.get("/menu/export", { responseType: "blob" });
}
