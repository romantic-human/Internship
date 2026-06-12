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


export function createDepartment(data: Partial<DeptItem>): Promise<DeptItem> {
  return request.post("/department/", data);
}

export function updateDepartment(id: number, data: Partial<DeptItem>): Promise<DeptItem> {
  return request.put(`/department/${id}`, data);
}

export function deleteDepartment(id: number): Promise<void> {
  return request.delete(`/department/${id}`);
}

export function updateDepartmentStatus(id: number, status: number): Promise<void> {
  return request.put(`/department/${id}/status`, { status });
}


export function batchSortDepartment(data: { id: number; sortOrder: number }[]): Promise<void> {
  return request.post("/department/batch-sort", data);
}

export function batchDeleteDepartments(ids: number[]): Promise<void> {
  return request.delete("/department/batch", { data: { ids } });
}

export function exportDepartments(): Promise<Blob> {
  return request.get("/department/export", { responseType: "blob" });
}


export function downloadDepartmentTemplate(): Promise<Blob> {
  return request.get("/department/template", { responseType: "blob" });
}

export function importDepartments(file: File): Promise<{ success: number; skipped: number; errors: string[] }> {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/department/import-departments", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
