import request from "@/utils/request";

export interface DataSource {
  id: number;
  name: string;
  db_type: string;
  host: string;
  port: number;
  db_name: string;
  username: string;
  password_enc: string;
  description: string;
  status: number;
  created_by: number | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface QueryHistory {
  id: number;
  user: number;
  datasource: number | null;
  datasource_name: string;
  question: string;
  generated_sql: string;
  execution_time: number;
  result_count: number;
  status: number;
  is_favorite: number;
  error_message: string;
  created_at: string;
}

export interface QueryResult {
  sql: string;
  columns: string[];
  rows: any[][];
  row_count: number;
  execution_time: number;
}

export interface TableMeta {
  table_name: string;
  table_comment: string;
  columns: { name: string; type: string; nullable: boolean; comment: string; is_primary: boolean }[];
}

export function getDataSourceList(params?: Record<string, any>): Promise<{ records: DataSource[]; total: number }> {
  return request.get("/nl2sql/datasource", { params });
}

export function getDataSource(id: number): Promise<DataSource> {
  return request.get(`/nl2sql/datasource/${id}`);
}

export function createDataSource(data: Partial<DataSource>): Promise<DataSource> {
  return request.post("/nl2sql/datasource", data);
}

export function updateDataSource(id: number, data: Partial<DataSource>): Promise<void> {
  return request.put(`/nl2sql/datasource/${id}`, data);
}

export function deleteDataSource(id: number): Promise<void> {
  return request.delete(`/nl2sql/datasource/${id}`);
}

export function testDataSourceConnection(id: number): Promise<void> {
  return request.post(`/nl2sql/datasource/${id}/test`);
}

export function getDataSourceTables(id: number): Promise<{ tables: TableMeta[] }> {
  return request.get(`/nl2sql/datasource/${id}/tables`);
}

export function getQueryHistoryList(params?: Record<string, any>): Promise<{ records: QueryHistory[]; total: number }> {
  return request.get("/nl2sql/history", { params });
}

export function deleteQueryHistory(id: number): Promise<void> {
  return request.delete(`/nl2sql/history/${id}`);
}

export function toggleQueryHistoryFavorite(id: number): Promise<void> {
  return request.put(`/nl2sql/history/${id}/favorite`);
}

export function executeQuery(datasourceId: number, question: string): Promise<QueryResult> {
  return request.post("/nl2sql/query", { datasource_id: datasourceId, question });
}
