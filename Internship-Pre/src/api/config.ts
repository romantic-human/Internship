import request from "@/utils/request";

export function getConfigList(params: any) {
  return request.get("/config", { params });
}

export function getConfigDetail(id: number) {
  return request.get(`/config/${id}`);
}

export function getConfigByKey(key: string) {
  return request.get("/config/by-key/", { params: { key } });
}

export function createConfig(data: any) {
  return request.post("/config", data);
}

export function updateConfig(id: number, data: any) {
  return request.put(`/config/${id}`, data);
}

export function deleteConfig(id: number) {
  return request.delete(`/config/${id}`);
}

export function updateConfigSort(id: number, sortOrder: number) {
  return request.put(`/config/${id}/sort`, { sortOrder });
}

export function batchSortConfig(data: { id: number; sortOrder: number }[]) {
  return request.post("/config/batch-sort", data);
}
