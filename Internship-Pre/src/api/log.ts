import request from "@/utils/request";

export interface LogItem {
  id: number;
  username: string;
  module: string;
  operation: string;
  method: string;
  request_url: string;
  request_params: string;
  response_result: string;
  ip: string;
  status: number;
  execution_time: number;
  create_time: string;
}

export interface LogListParams {
  page?: number;
  pageSize?: number;
  username?: string;
  module?: string;
  operation?: string;
  method?: string;
  status?: number;
  startTime?: string;
  endTime?: string;
}

export function getLogList(params: LogListParams): Promise<{ records: LogItem[]; total: number }> {
  return request.get("/log/", { params });
}

export function getLogDetail(id: number): Promise<LogItem> {
  return request.get(`/log/${id}`);
}

export function clearLogs(): Promise<void> {
  return request.delete("/log/clear");
}

export function exportLogs(params?: LogListParams): Promise<Blob> {
  return request.get("/log/export", { params, responseType: "blob" });
}
