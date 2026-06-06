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

export function getDepartmentDetail(id: number) {
  return request.get(`/department/${id}`);
}

export function createDepartment(data: Partial<DeptItem>) {
  return request.post("/department/", data);
}

export function updateDepartment(id: number, data: Partial<DeptItem>) {
  return request.put(`/department/${id}`, data);
}

export function deleteDepartment(id: number) {
  return request.delete(`/department/${id}`);
}

export function updateDepartmentStatus(id: number, status: number) {
  return request.put(`/department/${id}/status`, { status });
}

export function updateDepartmentSort(id: number, sortOrder: number) {
  return request.put(`/department/${id}/sort`, { sortOrder });
}

export function batchSortDepartment(data: { id: number; sortOrder: number }[]) {
  return request.post("/department/batch-sort", data);
}

export function batchDeleteDepartments(ids: number[]) {
  return request.delete("/department/batch", { data: { ids } });
}

export function exportDepartments() {
  return request.get("/department/export", { responseType: "blob" });
}