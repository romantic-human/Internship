import request from "@/utils/request";

export function getDepartmentTree() {
  return request.get("/department/tree");
}

export function getDepartmentDetail(id: number) {
  return request.get(`/department/${id}`);
}

export function createDepartment(data: any) {
  return request.post("/department", data);
}

export function updateDepartment(id: number, data: any) {
  return request.put(`/department/${id}`, data);
}

export function deleteDepartment(id: number) {
  return request.delete(`/department/${id}`);
}

export function updateDepartmentStatus(id: number, status: number) {
  return request.put(`/department/${id}/status`, { status });
}
