import request from "@/utils/request";

// ─── 字典类型 ─────────────────────────────────────────────

export interface DictType {
  id: number;
  dict_name: string;
  dict_type: string;
  status: number;
  remark: string;
  create_time: string;
  update_time: string;
}

export interface DictTypeListParams {
  page?: number;
  pageSize?: number;
  dict_name?: string;
  dict_type?: string;
}

export function getDictTypeList(params: DictTypeListParams): Promise<{ records: DictType[]; total: number }> {
  return request.get("/dict/type", { params });
}

export function getDictTypeDetail(id: number): Promise<DictType> {
  return request.get(`/dict/type/${id}`);
}

export function createDictType(data: Partial<DictType>): Promise<DictType> {
  return request.post("/dict/type", data);
}

export function updateDictType(id: number, data: Partial<DictType>): Promise<DictType> {
  return request.put(`/dict/type/${id}`, data);
}

export function deleteDictType(id: number): Promise<void> {
  return request.delete(`/dict/type/${id}`);
}

export function batchDeleteDictTypes(ids: number[]): Promise<void> {
  return request.delete("/dict/type/batch", { data: { ids } });
}

export function updateDictTypeStatus(id: number, status: number): Promise<void> {
  return request.put(`/dict/type/${id}/status`, { status });
}

export function exportDictTypes(): Promise<Blob> {
  return request.get("/dict/type/export", { responseType: "blob" });
}

// ─── 字典数据 ─────────────────────────────────────────────

export interface DictData {
  id: number;
  dict_type: string;
  dict_type_name: string;
  dict_label: string;
  dict_value: string;
  css_class: string;
  list_class: string;
  sort_order: number;
  status: number;
  is_default: boolean;
  remark: string;
  create_time: string;
  update_time: string;
}

export interface DictDataListParams {
  page?: number;
  pageSize?: number;
  dict_type?: string;
  dict_label?: string;
  status?: number;
}

export function getDictDataList(params: DictDataListParams): Promise<{ records: DictData[]; total: number }> {
  return request.get("/dict/data", { params });
}

export function getDictDataDetail(id: number): Promise<DictData> {
  return request.get(`/dict/data/${id}`);
}

export function createDictData(data: Partial<DictData>): Promise<DictData> {
  return request.post("/dict/data", data);
}

export function updateDictData(id: number, data: Partial<DictData>): Promise<DictData> {
  return request.put(`/dict/data/${id}`, data);
}

export function deleteDictData(id: number): Promise<void> {
  return request.delete(`/dict/data/${id}`);
}

export function batchDeleteDictData(ids: number[]): Promise<void> {
  return request.delete("/dict/data/batch", { data: { ids } });
}

export function updateDictDataStatus(id: number, status: number): Promise<void> {
  return request.put(`/dict/data/${id}/status`, { status });
}

/** 根据字典类型编码获取全部启用的数据项（用于下拉框） */
export function getDictDataByType(dictType: string): Promise<DictData[]> {
  return request.get(`/dict/data/type/${dictType}`);
}
