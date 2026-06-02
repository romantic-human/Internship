import request from "@/utils/request";

export function getConfigList(params: any) {
  return request.get("/config/list", { params });
}

export function getConfigDetail(id: number) {
  return request.get(`/config/${id}`);
}

export function getConfigByKey(key: string) {
  return request.get(`/config/by-key/${key}`);
}

export function createConfig(data: any) {
  return request.post("/config", data);
}

export function updateConfig(id: number, data: any) {
  return request.put(`/config/${id}`, data);
}