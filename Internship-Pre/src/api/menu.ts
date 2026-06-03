import request from "@/utils/request";

export function getMenuTree() {
  return request.get("/menu/tree");
}

export function getMenuDetail(id: number) {
  return request.get(`/menu/${id}`);
}

export function createMenu(data: any) {
  return request.post("/menu", data);
}

export function updateMenu(id: number, data: any) {
  return request.put(`/menu/${id}`, data);
}

export function deleteMenu(id: number) {
  return request.delete(`/menu/${id}`);
}

export function updateMenuStatus(id: number, status: number) {
  return request.put(`/menu/${id}/status`, { status });
}

export function updateMenuSort(id: number, sortOrder: number) {
  return request.put(`/menu/${id}/sort`, { sortOrder });
}

export function batchSortMenu(data: { id: number; sortOrder: number }[]) {
  return request.post("/menu/batch-sort", data);
}

export function getMenuOptions() {
  return request.get("/menu/options");
}
