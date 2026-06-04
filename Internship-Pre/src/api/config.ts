import request from "@/utils/request";

export interface ConfigItem {
  id: number;
  config_name: string;
  config_key: string;
  config_value: string;
  config_type: number;
  sort_order: number;
  status: number;
  create_time: string;
}

export function getConfigList(params: Record<string, any>): Promise<{ records: ConfigItem[]; total: number }> {
  return request.get("/config/", { params });
}

export function getConfigDetail(id: number): Promise<ConfigItem> {
  return request.get(`/config/${id}`);
}

export function createConfig(data: Partial<ConfigItem>) {
  return request.post("/config/", data);
}

export function updateConfig(id: number, data: Partial<ConfigItem>) {
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