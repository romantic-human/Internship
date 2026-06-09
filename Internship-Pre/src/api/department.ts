import request from "@/utils/request";

export interface DeptItem {
  id: number;
  parent_id: number | null;
  dept_name: string;
  leader: string;
  phone: string;
  email: string;
  sort_order: number;
  status: number;
  create_time: string;
  update_time: string;
  children?: DeptItem[];
}

export function getDepartmentTree(): Promise<DeptItem[]> {
  return request.get("/department/tree");
}

export function getDepartmentDetail(id: number): Promise<DeptItem> {
  return request.get(`/department/${id}`);
}

export function createDepartment(data: Partial<DeptItem>): Promise<DeptItem> {
  return request.post("/department/", data);
}

export function updateDepartment(id: number, data: Partial<DeptItem>): Promise<DeptItem> {
  return request.put(`/department/${id}`, data);
}

export function deleteDepartment(id: number): Promise<void> {
export function deleteDepartment(id: number): Promise<any> {
  return request.delete(`/department/${id}`);
}

export function updateDepartmentStatus(id: number, status: number): Promise<void> {
export function updateDepartmentStatus(id: number, status: number): Promise<any> {
  return request.put(`/department/${id}/status`, { status });
}

export function updateDepartmentSort(id: number, sortOrder: number): Promise<void> {
export function updateDepartmentSort(id: number, sortOrder: number): Promise<any> {
  return request.put(`/department/${id}/sort`, { sortOrder });
}

export function batchSortDepartment(data: { id: number; sortOrder: number }[]): Promise<void> {
export function batchSortDepartment(data: { id: number; sortOrder: number }[]): Promise<any> {
  return request.post("/department/batch-sort", data);
}

export function batchDeleteDepartments(ids: number[]): Promise<void> {
export function batchDeleteDepartments(ids: number[]): Promise<any> {
  return request.delete("/department/batch", { data: { ids } });
}

export function exportDepartments(): Promise<Blob> {
  return request.get("/department/export", { responseType: "blob" });

}
