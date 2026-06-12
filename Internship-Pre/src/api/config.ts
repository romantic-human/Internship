import request from "@/utils/request";

export interface ConfigItem {
  id: number;
  config_name: string;
  config_key: string;
  config_value: string;
  config_type: number;
  sort_order: number;
  status: number;
  remark: string;
  create_time: string;
  update_time: string;
}

export interface ConfigListParams {
  page?: number;
  pageSize?: number;
  config_name?: string;
  config_key?: string;
}

export function getConfigList(params: ConfigListParams): Promise<{ records: ConfigItem[]; total: number }> {
  return request.get("/config/", { params });
}

export function getConfigDetail(id: number): Promise<ConfigItem> {
  return request.get(`/config/${id}`);
}

export function createConfig(data: Partial<ConfigItem>): Promise<ConfigItem> {
  return request.post("/config/", data);
}

export function updateConfig(id: number, data: Partial<ConfigItem>): Promise<ConfigItem> {
  return request.put(`/config/${id}`, data);
}

export function deleteConfig(id: number): Promise<void> {
  return request.delete(`/config/${id}`);
}

export function updateConfigStatus(id: number, status: number): Promise<void> {
  return request.put(`/config/${id}/status`, { status });
}

export function updateConfigSort(id: number, sortOrder: number): Promise<void> {
  return request.put(`/config/${id}/sort`, { sortOrder });
}

export function batchSortConfig(data: { id: number; sortOrder: number }[]): Promise<void> {
  return request.post("/config/batch-sort", data);
}

export function batchDeleteConfigs(ids: number[]): Promise<void> {
  return request.delete("/config/batch", { data: { ids } });
}

export function exportConfigs(): Promise<Blob> {
  return request.get("/config/export", { responseType: "blob" });
}

export function downloadConfigTemplate(): Promise<Blob> {
  return request.get("/config/template", { responseType: "blob" });
}

export function importConfigs(file: File): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  return request.post("/config/import", form);
}
