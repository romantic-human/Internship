import request from "@/utils/request";

export function getLogList(params: any) {
  return request.get("/log/list", { params });
}

export function getLogDetail(id: number) {
  return request.get(`/log/${id}`);
}

export function clearLogs() {
  return request.delete("/log");
}

export function exportLogs(params: any) {
  return request.get("/log/export", { params, responseType: "blob" });
}
